#!/usr/bin/env python3

#wakemeup is a command line utility to set up and keep track of timers
    
#    Copyright (C) 2020  Emre Şenliyim

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# The timer service. Exports a dbus service and exposes methods to
# set timers, and to cancel and remove them
# TODO alarms soon

from dbus_next.aio import MessageBus

from contextlib import closing
from TimerService import TimerInterface

import asyncio, re

#dbus constants
OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp.Timer"
BUS_NAME = "com.esenliyim.WakeMeUp"

#runs forever in an event loop
async def main():
    bus = await MessageBus().connect()
    interface = TimerInterface(IFACE, loop)
    bus.export(OPATH, interface)
    await bus.request_name(BUS_NAME)
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    with closing(asyncio.get_event_loop()) as loop:
        loop.run_until_complete(main())