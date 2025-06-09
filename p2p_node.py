import asyncio
from p2pd import *
import sys

# 👊 Your callback – reacts to incoming messages
async def msg_cb(msg, client_tup, pipe):
    print(f"\n[RECV] From {client_tup}: {msg.decode(errors='ignore')}")
    if b"PING" in msg:
        await pipe.send(b"PONG", client_tup)
    elif b"PONG" in msg:
        print(f"[INFO] Got PONG from {client_tup}")

# 👊 Send a message to all connected peers
async def broadcast_ping(node):
    while True:
        await asyncio.sleep(10)  # slap every 10s
        peers = await node.peers()
        for peer in peers:
            print(f"[SEND] PING to {peer}")
            await node.send(b"PING", peer)

# 👊 MAIN FUNCTION
async def main():
    # 👇 Replace this with your real NIC name from `ip addr`
    INTERFACE_NAME = "enp2s0"  # <-- change me on each machine if needed

    try:
        iface = await load_interface(INTERFACE_NAME)
        if iface is None:
            print(f"[FATAL] Interface {INTERFACE_NAME} could not be loaded.")
            sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Failed to load {INTERFACE_NAME}: {e}")
        sys.exit(1)

    node_conf = dict_child({
        "enable_upnp": False,
        "sig_pipe_no": SIGNAL_PIPE_NO,
    }, NET_CONF)

    # Fire up the node
    node = await P2PNode(ifs=[iface], port=1337, conf=node_conf)
    node.add_msg_cb(msg_cb)

    print(f"[BOOT] Node running on {INTERFACE_NAME}, port 1337")
    print(f"[INFO] Node ID: {node.id}")
    
    # Optional: print current peers every 10s
    asyncio.create_task(broadcast_ping(node))

    # Run forever
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Closing node.")
        await node.close()

# Run it like a demon
if __name__ == "__main__":
    asyncio.run(main())
