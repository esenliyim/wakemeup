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
    # returns an array of dictionaries
    # one dict() contains: timer id, remaining time(s), status(b),
    #   what happens when timer goes off
    @method()
    def showTimers(self) -> 'aa{ss}':
        active = []
        for f in TimerInterface._active_timers:
            t: Timer = TimerInterface._active_timers[f]
            timer = dict()
            timer['ID'] = t.id
            remaining: int
            if t.isRunning:
                remaining = int((t.end - datetime.now()).total_seconds())
            else:
                remaining = t.remaining
            timer['remaining'] = str(remaining)
            timer['when_finished'] = t.finalAction
            timer['isRunning'] = str(t.isRunning)
            active.append(timer)
        print("Reporting active")
        return active

    #removes the timer with the specified id
    @method()
    def removeTimer(self, id: 's') -> 'b':
        return TimerInterface.clearTimer(id)

    #pauses the timer with the specified id
    @method()
    def pauseTimer(self, id: 's') -> 'bs':
        if id not in TimerInterface._active_timers:
            errorMsg = "timer %s not found." % id
            return [False, errorMsg]
        timer: Timer = TimerInterface._active_timers[id]
        if timer.isRunning:
            timer.task.cancel()
            timer.isRunning = False
            remaining = int((timer.end - datetime.now()).total_seconds())
            timer.remaining = remaining
            return [True, "timer %s paused." % id]
        else:
            errorMsg = "timer %s is already paused." % id
            return [False, errorMsg]
            
    @method()
    def resumeTimer(self, id: 's') -> 'bs':
        if id not in TimerInterface._active_timers:
            errorMsg = "timer %s not found." % id
            return [False, errorMsg]
        timer: Timer = TimerInterface._active_timers[id]
        if timer.isRunning:
            errorMsg = "timer %s already running." % id
            return [False, errorMsg]
        else:
            remaining = timer.remaining
            timer.end = datetime.now() + timedelta(seconds=remaining)
            timer.setTask(loop.create_task(executeTimer(remaining)))
            timer.isRunning = True
            return [True, "timer %s is resuming." % id]

    #the method that cleans up the active timers list
    #called when a timer goes off and when a timer is to be manually removed
    def clearTimer(self, id):
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
        self.remaining = length
        self.finalAction = finalAction
        self.started = datetime.now()
        self.end = self.started + timedelta(seconds=length)
        self.isRunning = True
        # TODO leave adding to interface itself
        TimerInterface._active_timers[self.id] = self
    
    def setTask(self, task):
        self.task: asyncio.Task = task

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