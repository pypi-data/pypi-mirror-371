from __future__ import annotations
import asyncio
import sys


PROMPT = "> "


async def _reader_task(reader: asyncio.StreamReader):
    while not reader.at_eof():
        data = await reader.readline()
        if not data:
            break
        print(data.decode(errors="ignore"), end="")


async def _stdin_task(writer: asyncio.StreamWriter):
    loop = asyncio.get_running_loop()

    def _sync_readline() -> str:
        try:
            return sys.stdin.readline()
        except KeyboardInterrupt:
            return "/quit\n"

    while True:
        line = await loop.run_in_executor(None, _sync_readline)
        if not line:
            line = "/quit\n"
        writer.write(line.encode())
        try:
            await writer.drain()
        except Exception:
            return
        if line.strip().startswith("/quit"):
            return
        print(PROMPT, end="", flush=True)


async def run_client(host: str, port: int, name: str | None) -> int:
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except Exception as exc:
        print(f"Failed to connect to {host}:{port} — {exc}")
        return 2

    # Send nickname proactively after greeting prompt arrives
    async def send_name():
        # read until we see the nickname prompt or timeout
        try:
            line = await asyncio.wait_for(reader.readline(), timeout=5)
            if name is not None:
                writer.write((name + "\n").encode())
                await writer.drain()
            else:
                # print the rest of the greeting and show prompt
                print(line.decode(errors="ignore"), end="")
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
