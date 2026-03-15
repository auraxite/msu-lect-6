#!/usr/bin/env python3

import asyncio
import shlex
import cowsay

HOST = "0.0.0.0"
PORT = 1337

clients = {}
logged_users = set()


async def chat(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    me = f"anon_{id(writer)}"
    clients[me] = asyncio.Queue()

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients[me].get())

    while not reader.at_eof():
        done, pending = await asyncio.wait(
            [send, receive],
            return_when=asyncio.FIRST_COMPLETED
        )

        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())

                data = q.result()
                if not data:
                    continue
                line = data.decode().strip()
                if not line:
                    continue

                try:
                    args = shlex.split(line)
                except ValueError:
                    await clients[me].put("Invalid arguments")
                    continue

                match args:
                    case ["who"]:
                        if me not in logged_users:
                            await clients[me].put("Login first")
                        else:
                            await clients[me].put(" ".join(sorted(logged_users)))

                    case ["cows"]:
                        if me not in logged_users:
                            await clients[me].put("Login first")
                        else:
                            free = sorted(
                                cow for cow in cowsay.list_cows()
                                if cow not in logged_users
                            )
                            await clients[me].put(" ".join(free))

                    case ["login", cow]:
                        if me in logged_users:
                            await clients[me].put("You are logged in")
                        elif cow not in cowsay.list_cows():
                            await clients[me].put("No such cow")
                        elif cow in logged_users:
                            await clients[me].put("This login is occupied")
                        else:
                            clients[cow] = clients[me]
                            del clients[me]
                            me = cow
                            logged_users.add(me)
                            await clients[me].put(f"Logged in as {me}")

                    case ["say", target, *text_parts]:
                        if me not in logged_users:
                            await clients[me].put("Login first")
                        elif not text_parts:
                            await clients[me].put("Invalid arguments")
                        elif target not in logged_users:
                            await clients[me].put("No such user")
                        else:
                            message = cowsay.cowsay(" ".join(text_parts), cow=me)
                            await clients[target].put(message)

                    case ["yield", *text_parts]:
                        if me not in logged_users:
                            await clients[me].put("Login first")
                        elif not text_parts:
                            await clients[me].put("Invalid arguments")
                        else:
                            message = cowsay.cowsay(" ".join(text_parts), cow=me)
                            for user in logged_users:
                                if user != me:
                                    await clients[user].put(message)

                    case ["quit"]:
                        send.cancel()
                        receive.cancel()

                        if me in logged_users:
                            logged_users.remove(me)

                        print(me, "DONE")
                        del clients[me]
                        writer.close()
                        await writer.wait_closed()
                        return

                    case _:
                        if me not in logged_users:
                            await clients[me].put("Login first")
                        else:
                            await clients[me].put("Unknown command")

            elif q is receive:
                receive = asyncio.create_task(clients[me].get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()

    send.cancel()
    receive.cancel()

    if me in logged_users:
        logged_users.remove(me)

    print(me, "DONE")
    del clients[me]
    writer.close()
    await writer.wait_closed()


async def main() -> None:
    server = await asyncio.start_server(chat, HOST, PORT)
    async with server:
        await server.serve_forever()


asyncio.run(main())