from dbus_next.aio import MessageBus
from dbus_next import Variant

import asyncio

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp.Timer"
BUS_NAME = "com.esenliyim.WakeMeUp"

async def main():
    bus = await MessageBus().connect()
    bok = await bus.introspect('com.esenliyim.WakeMeUp', '/com/esenliyim/WakeMeUp')
    proxy = bus.get_proxy_object('com.esenliyim.WakeMeUp',
     '/com/esenliyim/WakeMeUp', bok)
    interface = proxy.get_interface('com.esenliyim.WakeMeUp.Timer')
    print(await interface.call_set_timer(30, 'asd'))
    print(await interface.call_set_timer(25, 'asd'))
    print(await interface.call_show_timers())

def main():
    bus = MessageBus().connect()
    introspect = bus.introspect(BUS_NAME, OPATH)
    proxy = bus.get_proxy_object(BUS_NAME, OPATH, introspect)
    interface = proxy.get_interface(IFACE)
    print(interface.call_set_timer(30, 'asd'))
    print(interface.call_set_timer(25, 'asd'))
    print(interface.call_show_timers())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())