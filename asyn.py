import asyncio
from p2pd.interface import list_interfaces, load_interfaces

async def main():
    names = await list_interfaces()
    print(f"[+] Found interfaces: {names}")
    ifs = await load_interfaces(names)
    for iface in ifs:
        print(f"[*] Interface: {iface.name}")
        for addr in iface.addrs:
            print(f"    - {addr.family}: {addr.ip}/{addr.prefixlen}")

asyncio.run(main())
