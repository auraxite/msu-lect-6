#!/usr/bin/env python3

import asyncio
import cmd
import contextlib
import cowsay
import sys

HOST = "127.0.0.1"
PORT = 1337


class Client(cmd.Cmd):
    prompt = "> "

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        super().__init__()
        self.loop = asyncio.get_running_loop()
        self.reader = reader
        self.writer = writer
        self.req_id = 1
        self.pending: dict[int, asyncio.Future[str]] = {}
        self.peers: list[str] = []

    async def send(self, line: str, expect_response: bool = False) -> str | None:
        if expect_response:
            rid = self.req_id
            self.req_id += 1
            msg = f"{rid} {line}\n"
            fut = self.loop.create_future()
            self.pending[rid] = fut
            self.writer.write(msg.encode())
            await self.writer.drain()
            return await fut
        self.writer.write(f"0 {line}\n".encode())
        await self.writer.drain()
        return None

    async def reader_task(self) -> None:
        while True:
            data = await self.reader.readline()
            if not data:
                break
            line = data.decode().strip()
            parts = line.split(" ", 1)
            try:
                rid = int(parts[0])
            except ValueError:
                print(line)
                continue
            payload = parts[1] if len(parts) > 1 else ""

            if rid == 0:
                print(payload)
            elif rid in self.pending:
                self.pending[rid].set_result(payload)
                del self.pending[rid]

    def run_async(self, coro, timeout: float = 10.0):
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return fut.result(timeout=timeout)
        except:
            return None

    def run_command(self, cmd_line: str) -> None:
        async def task() -> str | None:
            return await self.send(cmd_line, expect_response=True)

        res = self.run_async(task())
        if res is None:
            return
        print(res)
        parts = cmd_line.strip().split()
        if len(parts) >= 1 and parts[0] == "who" and res != "Login first":
            self.peers = res.split() if res else []

    def do_who(self, arg: str) -> None:
        self.run_command("who")

    def do_cows(self, arg: str) -> None:
        self.run_command("cows")

    def do_login(self, arg: str) -> None:
        self.run_command(f"login {arg}")

    def do_say(self, arg: str) -> None:
        self.run_command(f"say {arg}")

    def do_yield(self, arg: str) -> None:
        self.run_command(f"yield {arg}")

    def do_quit(self, arg: str) -> bool:
        async def q() -> None:
            await self.send("quit")

        self.run_async(q())
        return True

    def complete_login(self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        parts = line.split()
        if not parts or parts[0] != "login" or len(parts) > 2:
            return []
        if not text:
            return []
        cows = cowsay.list_cows()
        return [c for c in cows if c.startswith(text)]

    def complete_say(self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        parts = line.split()
        if not parts or parts[0] != "say" or len(parts) > 2:
            return []
        if not text:
            return []
        return [n for n in self.peers if n.startswith(text)]


async def main() -> None:
    reader, writer = await asyncio.open_connection(HOST, PORT)
    client = Client(reader, writer)
    reader_task = asyncio.create_task(client.reader_task())
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, client.cmdloop)
    finally:
        reader_task.cancel()
        try:
            await reader_task
        except asyncio.CancelledError:
            pass
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass


asyncio.run(main())
