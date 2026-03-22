#!/usr/bin/env python3

import asyncio
import cmd

HOST = "127.0.0.1"
PORT = 1337


class ChatClient(cmd.Cmd):
    prompt = "> "

    def __init__(self, reader, writer):
        super().__init__()
        self.loop = asyncio.get_running_loop()
        self.reader = reader
        self.writer = writer
        self.req_id = 1
        self.pending = {}

    async def send(self, line, expect_response=False) -> str | None:
        if expect_response:
            rid = self.req_id
            self.req_id += 1
            msg = f"{rid} {line}\n"
            fut = self.loop.create_future()
            self.pending[rid] = fut
            self.writer.write(msg.encode())
            await self.writer.drain()
            return await fut
        else:
            self.writer.write(f"0 {line}\n".encode())
            await self.writer.drain()

    async def reader_task(self) -> None:
        while True:
            data = await self.reader.readline()
            if not data:
                break

            line = data.decode().strip()

            try:
                rid_str, payload = line.split(" ", 1)
                rid = int(rid_str)
            except:
                print(line)
                continue

            if rid == 0:
                print(payload)
            elif rid in self.pending:
                self.pending[rid].set_result(payload)
                del self.pending[rid]

async def main() -> None:
    reader, writer = await asyncio.open_connection(HOST, PORT)
    client = ChatClient(reader, writer)

    asyncio.create_task(client.reader_task())

    await asyncio.get_event_loop().run_in_executor(None, client.cmdloop)


asyncio.run(main())