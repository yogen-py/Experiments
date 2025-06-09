import asyncio
from p2pd import P2PNode, NET_CONF, SIGNAL_PIPE_NO
from p2pd.interface import list_interfaces, load_interfaces

async def msg_cb(msg, client_tup, pipe):
    print(f"\n[RECV] From {client_tup}: {msg.decode(errors='ignore')}")
    if b"PING" in msg:
        print(f"[RESPONDING] -> PONG to {client_tup}")
        await pipe.send(b"PONG", client_tup)

async def periodic_ping(node):
    await asyncio.sleep(5)
    peers = await node.peers()
    print(f"[DEBUG] Known peers: {peers}")
    for p in peers:
        print(f"[SEND] -> PING {p}")
        await node.send(b"PING", p)
    asyncio.create_task(periodic_ping(node))

async def main():
    print("[DEBUG] Scanning interfaces...")
    names = await list_interfaces()
    print(f"[DEBUG] Found interface names: {names}")
    if not names:
        print("[FATAL] No interfaces found")
        return

    print("[DEBUG] Loading interfaces...")
    ifs = await load_interfaces(names)
    print(f"[DEBUG] Loaded interfaces: {[iface.name for iface in ifs]}")
    for iface in ifs:
        print(f"  -> {iface.name}: {iface.addrs}")

    if not ifs:
        print("[FATAL] No valid interfaces loaded")
        return

    conf = dict_child({"enable_upnp": False, "sig_pipe_no": SIGNAL_PIPE_NO}, NET_CONF)
    node = await P2PNode(ifs=ifs, port=1337, conf=conf)
    node.add_msg_cb(msg_cb)

    print(f"[DEBUG] Node started. ID={node.id}, Port=1337")
    asyncio.create_task(periodic_ping(node))

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("[DEBUG] Shutting down node.")
        await node.close()

if __name__ == "__main__":
    asyncio.run(main())
