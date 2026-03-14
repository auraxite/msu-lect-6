#!/usr/bin/env python3

import asyncio
import shlex
import cowsay

HOST = "0.0.0.0"
PORT = 1337



async def chat(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    pass


async def main() -> None:
    server = await asyncio.start_server(chat, HOST, PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())