from dbus_next.aio import MessageBus
from dbus_next.service import (ServiceInterface,
                               method, dbus_property, signal)
from dbus_next import Variant, DBusError
from gi.repository import Notify
from contextlib import closing
from datetime import datetime, timedelta

import asyncio

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp.Timer"
BUS_NAME = "com.esenliyim.WakeMeUp"

class TimerInterface(ServiceInterface):

    _active_timers = dict()

    def __init__(self):
        super().__init__(IFACE)
        print("oldu")

    @method()
    def setTimer(self, length: 'i', msg: 's') -> 's':
        timer = Timer(length, msg)
        timer.setTask(loop.create_task(executeTimer(timer)))
        return str(len(TimerInterface._active_timers))

    @method()
    def showTimers(self) -> 'aa{ss}':
        active = []
        for f in TimerInterface._active_timers:
            t = TimerInterface._active_timers[f]
            timer = dict()
            timer['ID'] = t.id
            remaining = t.end - datetime.now()
            timer['remaining'] = str(remaining)
            timer['when_finished'] = t.finalAction
            active.append(timer)
        print("Reporting active")
        return active

    @method()
    def removeTimer(self, id: 's') -> 'b':
        return TimerInterface.clearTimer(id)

    def clearTimer(id):
        if id in TimerInterface._active_timers:
            task = TimerInterface._active_timers[id].task
            task.cancel()
            TimerInterface._active_timers.pop(id)
            return True
        else:
            return False

async def executeTimer(timer):
    await asyncio.sleep(timer)
    await TimerInterface.clearTimer(timer.id)


#async def clearTimer(id):
#    if id in TimerInterface._active_timers:
#        task = TimerInterface._active_timers[id].task
#        task.cancel()
#        TimerInterface._active_timers.pop(id)
#        return True
#    else:
#        return False

class Timer():

    ids = 1

    def __init__(self, length: int, finalAction):
        self.id = "t" + str(Timer.ids)
        Timer.ids += 1
        self.length = length
        self.finalAction = finalAction
        self.started = datetime.now()
        self.end = self.started + timedelta(seconds=length)
        TimerInterface._active_timers[self.id] = self
    
    def setTask(self, task):
        self.task = task

async def main():
    bus = await MessageBus().connect()
    interface = TimerInterface()
    bus.export(OPATH, interface)
    await bus.request_name(BUS_NAME)
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    with closing(asyncio.get_event_loop()) as loop:
        loop.run_until_complete(main())