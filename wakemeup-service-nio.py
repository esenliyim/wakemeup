#!/usr/bin/env python3

# The timer service. Exports a dbus service and exposes methods to
# set timers, and to cancel and remove them
# TODO alarms soon

from dbus_next.aio import MessageBus
from dbus_next.service import (ServiceInterface,
                               method, dbus_property, signal)
from dbus_next import Variant, DBusError
from gi.repository import Notify
from contextlib import closing
from datetime import datetime, timedelta

import asyncio

#dbus constants
OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp.Timer"
BUS_NAME = "com.esenliyim.WakeMeUp"

#the actual dbus service that gets exported
class TimerInterface(ServiceInterface):

    _active_timers = dict()

    def __init__(self):
        super().__init__(IFACE)
        print("Service started")

    #set a new timer with the specified duration and the message
    #lenght:int is the duration, msg:str is the message
    @method()
    def setTimer(self, length: 'i', msg: 's') -> 's':
        timer = Timer(length, msg)
        timer.setTask(loop.create_task(executeTimer(timer)))
        #TODO a proper response, not just the number of active timers
        return str(len(TimerInterface._active_timers))

    #shows currently active timers
    #returns an array of dictionaries
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

    #removes the timer with the specified id
    @method()
    def removeTimer(self, id: 's') -> 'b':
        return TimerInterface.clearTimer(id)

    #the method that cleans up the active timers list
    #called when a timer goes off and when a timer is to be manually removed
    def clearTimer(id):
        if id in TimerInterface._active_timers:
            task = TimerInterface._active_timers[id].task
            task.cancel()
            TimerInterface._active_timers.pop(id)
            return True
        else:
            return False

#start counting down
#TODO not happy with it, find a better way maybe?
async def executeTimer(timer):
    await asyncio.sleep(timer)
    await TimerInterface.clearTimer(timer.id)

#the class for timer objects
#length:int is how long they run,
# finalAction:(for now)str is the message to be displayed afterwards
# started:datetime is when the timer was started
# end:datetime is when it's supposed to end
# TODO implement custom actions as finalAction, like running shell commands
class Timer():

    # to keep track of names
    # TODO find a better way of naming things
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

#runs forever in an event loop
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