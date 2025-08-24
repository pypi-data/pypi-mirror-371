from __future__ import annotations
import asyncio
import signal
from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass
from typing import Dict

WELCOME = (
    "Welcome to terminalchate!\n"
    "Type messages and press Enter to chat.\n"
    "Commands: /nick <name>, /quit\n"
)

@dataclass
class Peer:
    name: str
    reader: StreamReader
    writer: StreamWriter

class ChatServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 7777, *, max_clients: int | None = None):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self._peers: Dict[str, Peer] = {}
        self._server: asyncio.base_events.Server | None = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
        sockets = ", ".join(str(s.getsockname()) for s in (self._server.sockets or []))
        print(f"terminalchate-server listening on {sockets}")
        async with self._server:
            await self._server.serve_forever()

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

    async def _broadcast(self, msg: str, *, exclude: str | None = None) -> None:
        async with self._lock:
            for name, peer in list(self._peers.items()):
                if name == exclude:
                    continue
                try:
                    peer.writer.write(msg.encode() + b"\n")
                    await peer.writer.drain()
                except Exception:
                    await self._disconnect(name, reason="write-failed")

    async def _disconnect(self, name: str, *, reason: str = "") -> None:
        peer = self._peers.pop(name, None)
        if peer:
            try:
                peer.writer.close()
                await peer.writer.wait_closed()
            finally:
                await self._broadcast(f"* {name} left ({reason}) *")

    async def _handle_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        addr = writer.get_extra_info("peername")
        default_name = f"user_{addr[1]}" if addr else "user"

        # Greeting
        writer.write(WELCOME.encode())
        writer.write(f"Enter your nickname [{default_name}]: ".encode())
        await writer.drain()

        # Read nickname (single line, with timeout)
        name = default_name
        try:
            line = await asyncio.wait_for(reader.readline(), timeout=30)
            if line:
                proposed = line.decode().strip() or default_name
                # sanitize spaces/newlines
                proposed = "".join(ch for ch in proposed if ch.isprintable()).strip()
                if proposed:
                    name = proposed[:32]
        except asyncio.TimeoutError:
            pass

        # Ensure unique nickname
        suffix = 1
        base = name
        async with self._lock:
            while name in self._peers:
                suffix += 1
                name = f"{base}_{suffix}"
            self._peers[name] = Peer(name, reader, writer)

        await self._broadcast(f"* {name} joined *")
        writer.write(f"You are known as {name}. Say hi!\n".encode())
        await writer.drain()

        try:
            while not reader.at_eof():
                raw = await reader.readline()
                if not raw:
                    break
                text = raw.decode(errors="ignore").rstrip("\r\n")
                if not text:
                    continue

                if text.startswith("/quit"):
                    break
                if text.startswith("/nick "):
                    new_name = text.split(" ", 1)[1].strip() or name
                    new_name = new_name[:32]
                    async with self._lock:
                        if new_name in self._peers:
                            writer.write(b"Nickname in use.\n")
                        else:
                            self._peers.pop(name, None)
                            self._peers[new_name] = Peer(new_name, reader, writer)
                            await self._broadcast(f"* {name} is now {new_name} *")
                            name = new_name
                    await writer.drain()
                    continue

                await self._broadcast(f"[{name}] {text}", exclude=name)
        except Exception as exc:
            print(f"client error for {name}: {exc}")
        finally:
            await self._disconnect(name, reason="quit")

def _install_signal_handlers(server: ChatServer) -> None:
    loop = asyncio.get_running_loop()

    def _stop() -> None:
        # Nicht blockieren: Stop asynchron anstoßen
        asyncio.create_task(server.stop())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            # Windows kann SIGTERM nicht unterstützen
            pass

def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(prog="terminalchate-server", description="Run a tiny terminal chat server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=7777, help="Port to listen on (default: 7777)")
    parser.add_argument("--max-clients", type=int, default=None, help="Optional limit on concurrent clients")
    args = parser.parse_args(argv)

    server = ChatServer(args.host, args.port, max_clients=args.max_clients)

    async def runner():
        _install_signal_handlers(server)
        try:
            await server.start()
        except asyncio.CancelledError:
            pass

    asyncio.run(runner())

if __name__ == "__main__":
    main()
