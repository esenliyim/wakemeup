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

import asyncio, re, notify2, asyncio_glib

from dbus_next.aio import MessageBus
from dbus_next.service import (ServiceInterface, method, dbus_property)
from dbus_next import Variant, DBusError
from dbus_next.constants import ErrorType
from dbus import DBusException
from contextlib import closing
from datetime import datetime, timedelta
from Timer import Timer

#dbus constants
OPATH = "/com/esenliyim/WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"
IFACE = BUS_NAME + ".Timer"

class TimerInterface(ServiceInterface):

    _active_timers = dict()
    _ids = 0

    def __init__(self, interfaceName, loop):
        super().__init__(interfaceName)
        self._loop = loop
        print("Service started")

    #set a new timer with the specified duration and the message
    #lenght:int is the duration, msg:str is the message
    @method()
    def setTimer(self, length: 'i', msg: 's', cmd: 's') -> 'bs':
        try:
            # TODO kwargify self.task
            newId = self.makeId()
            timer = Timer(length, newId, _message=msg, _command=cmd)
            TimerInterface._active_timers[newId] = timer
            timer.task = self._loop.create_task(self.executeTimer(timer))  
            return [True, newId]
        except DBusException as e:
            return [False, str(e)]

    #shows currently active timers
    # returns an array of dictionaries
    # one dict() contains: timer id, remaining time(s), status(b),
    #   what happens when timer goes off
    @method()
    def showTimers(self) -> 'aa{ss}':
        active = []
        for f in TimerInterface._active_timers:
            t = TimerInterface._active_timers[f]
            timer = dict()
            timer['ID'] = t.id
            remaining: int
            if t.isRunning:
                remaining = int((t.end - datetime.now()).total_seconds())
            else:
                remaining = t.remaining
            timer['remaining'] = str(remaining)
            timer['isRunning'] = str(t.isRunning)
            if hasattr(t, 'message'):
                timer['message'] = t.message
            if hasattr(t, 'command'):
                timer['command'] = t.command
            active.append(timer)
        return active

    #removes the timer with the specified id
    @method()
    def removeTimer(self, id: 's') -> 'b':
        return self.clearTimer(id)

    #pauses the timer with the specified id
    @method()
    def pauseTimer(self, id: 's') -> 'bs':
        if id not in TimerInterface._active_timers:
            raise DBusError(ErrorType.FAILED, 'timer %s not found' % id)
        timer: Timer = TimerInterface._active_timers[id]
        if timer.isRunning:
            timer.task.cancel()
            timer.isRunning = False
            remaining = int((timer.end - datetime.now()).total_seconds())
            timer.remaining = remaining
            return [True, "timer %s paused." % id]
        else:
            raise DBusError(ErrorType.FAILED, 'timer %s already paused' % id)
            
    @method()
    def resumeTimer(self, id: 's') -> 'bs':
        if id not in TimerInterface._active_timers:
            raise DBusError(ErrorType.FAILED, "timer %s not found" % id)
        timer: Timer = TimerInterface._active_timers[id]
        if timer.isRunning:
            raise DBusError(ErrorType.FAILED, "timer %s already running" % id)
        else:
            remaining = timer.remaining
            timer.end = datetime.now() + timedelta(seconds=remaining)
            timer.setTask(_loop.create_task(executeTimer(remaining)))
            timer.isRunning = True
            return [True, "timer %s is resuming." % id]

    #the method that cleans up the active timers list
    #called when a timer goes off and when a timer is to be manually removed
    def clearTimer(self, id) -> bool:
        if id in TimerInterface._active_timers:
            task = TimerInterface._active_timers[id].task
            task.cancel()
            TimerInterface._active_timers.pop(id)
            return True
        else:
            return False
    
    #start counting down
    #TODO not happy with it, find a better way maybe?
    async def executeTimer(self, timer):
        await asyncio.sleep(timer.remaining)
        await self.setOffTimer(timer)
    
    async def setOffTimer(self, timer: Timer):
        if hasattr(timer, 'message'):
            try:
                notify2.init("WakeMeUp", self._loop)
                notification = notify2.Notification(
                    "Time is up!",
                    timer.message,
                    "dialog-information",
                )
                notification.add_action(
                    "clicked",
                    "Dismiss",
                    self.bokebok,
                    None
                )
                notification.set_timeout(notify2.EXPIRES_NEVER)
                notification.show()
            except Exception as e:
                print(e)

    # generates ID for a new timer
    def makeId(self) -> str:
        if not TimerInterface._active_timers:
            TimerInterface._ids = 1
            return "t1"
        TimerInterface._ids += 1
        return ("t%i" % TimerInterface._ids)

    def bokebok(self, notification, action_name, data):
        print("bokebok")

    # TODO
    def buttonCallback(self):
        pass

#runs forever in an event loop
async def main():

    #print(OPATH)
    #print(BUS_NAME)
    #print(IFACE)

    #create and export the dbus service
    bus = await MessageBus().connect()
    interface = TimerInterface(IFACE, loop)
    bus.export(OPATH, interface)
    await bus.request_name(BUS_NAME)
    await asyncio.get_event_loop().create_future()
    
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio_glib.GLibEventLoopPolicy())
    with closing(asyncio.get_event_loop()) as loop:
        loop.run_until_complete(main())