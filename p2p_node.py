import asyncio
from p2pd import *
from p2pd.interface import list_interfaces, load_interfaces

# 🧠 Callback when a message arrives
async def msg_cb(msg, client_tup, pipe):
    print(f"\n[RECV] From {client_tup}: {msg.decode(errors='ignore')}")
    if b"PING" in msg:
        print(f"[RESPONDING] Sending PONG to {client_tup}")
        await pipe.send(b"PONG", client_tup)
    elif b"PONG" in msg:
        print(f"[INFO] Got PONG from {client_tup}")

# 🧠 Periodically send PING to all known peers
async def broadcast_ping(node):
    while True:
        await asyncio.sleep(10)  # every 10 seconds
        peers = await node.peers()
        if peers:
            print(f"[PEERS] Currently connected to: {peers}")
        else:
            print("[PEERS] No connected peers found.")

        for peer in peers:
            print(f"[SEND] PING to {peer}")
            await node.send(b"PING", peer)

# 🧠 Main runner
async def main():
    print("[BOOT] Listing interfaces...")
    if_names = await list_interfaces()
    ifs = await load_interfaces(if_names)

    if not ifs:
        raise Exception("No valid network interfaces loaded. Check your NICs.")

    node_conf = dict_child({
        "enable_upnp": False,  # we’re on LAN, we don’t need this
        "sig_pipe_no": SIGNAL_PIPE_NO,
    }, NET_CONF)

    node = await P2PNode(ifs=ifs, port=1337, conf=node_conf)
    node.add_msg_cb(msg_cb)

    print(f"[STARTED] P2P Node is running on port 1337")
    print(f"[NODE ID] {node.id}")

    # Start periodic PING broadcast
    asyncio.create_task(broadcast_ping(node))

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Killing node...")
        await node.close()

if __name__ == "__main__":
    asyncio.run(main())
