from __future__ import annotations
import asyncio
import sys


PROMPT = "> "


async def _reader_task(reader: asyncio.StreamReader):
    """
    Task to read data from the server and print it to the console.
    """
    while not reader.at_eof():
        data = await reader.readline()
        if not data:
            break
        print(data.decode(errors="ignore"), end="")


async def _stdin_task(writer: asyncio.StreamWriter):
    """
    Task to read user input from stdin and send it to the server.
    """
    loop = asyncio.get_running_loop()

    def _sync_readline() -> str:
        """
        Synchronous readline function to run in a separate thread.
        """
        try:
            return sys.stdin.readline()
        except KeyboardInterrupt:
            return "/quit\n"

    while True:
        line = await loop.run_in_executor(None, _sync_readline)
        if not line:
            line = "/quit\n"

        # Handle client-side commands
        if line.strip().startswith("/help"):
            print("Commands:")
            print("  /nick <name> - change your nickname")
            print("  /quit        - leave the chat")
            print("  /help        - show this help message")
            print(PROMPT, end="", flush=True)
            continue

        writer.write(line.encode())
        try:
            await writer.drain()
        except Exception:
            return

        if line.strip().startswith("/quit"):
            return
        print(PROMPT, end="", flush=True)


async def run_client(host: str, port: int, name: str | None) -> int:
    """
    Main function to run the chat client.
    """
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except Exception as exc:
        print(f"Failed to connect to {host}:{port} — {exc}")
        return 2

    async def send_name():
        """
        Sends the nickname to the server after receiving the initial greeting.
        """
        try:
            await asyncio.wait_for(reader.readline(), timeout=5)
            if name is not None:
                writer.write((name + "\n").encode())
                await writer.drain()
        except asyncio.TimeoutError:
            if name is not None:
                writer.write((name + "\n").encode())
                await writer.drain()

    await send_name()

    print(PROMPT, end="", flush=True)
    tasks = [
        asyncio.create_task(_reader_task(reader)),
        asyncio.create_task(_stdin_task(writer)),
    ]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()
    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass
    return 0


def main(argv: list[str] | None = None) -> None:
    """
    Main entry point for the client script.
    """
    import argparse

    parser = argparse.ArgumentParser(prog="terminalchate", description="Connect to a terminalchat server")
    parser.add_argument("host", help="Server host")
    parser.add_argument("port", type=int, help="Server port")
    parser.add_argument("--name", help="Optional nickname to use")
    args = parser.parse_args(argv)

    code = asyncio.run(run_client(args.host, args.port, args.name))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
