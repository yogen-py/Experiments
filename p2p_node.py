import asyncio
from p2pd import *
import sys

# Handle incoming messages
async def msg_cb(msg, client_tup, pipe):
    print(f"[RECV from {client_tup}]: {msg.decode()}")
    if b"PING" in msg:
        await pipe.send(b"PONG", client_tup)

async def main():
    # Load interfaces and create node
    if_names = await list_interfaces()
    ifs = await load_interfaces(if_names)

    node = await P2PNode(ifs=ifs, port=1337)
    node.add_msg_cb(msg_cb)

    print(f"Node running on port 1337 with ID: {node.node_id}")

    async def stdin_loop():
        while True:
            try:
                data = input("Enter <ip> <msg>: ")
                ip, *msg = data.strip().split()
                msg = " ".join(msg).encode()
                await node.send(msg, (ip, 1337))
            except Exception as e:
                print(f"Error: {e}")

    await stdin_loop()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[!] Exiting like a legend.")
