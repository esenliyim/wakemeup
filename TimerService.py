from datetime import timedelta, datetime
from dbus_next.service import (ServiceInterface,
                               method, dbus_property)
from dbus_next import Variant, DBusError
from dbus_next.constants import ErrorType as ERRORS
from dbus_next.constants import MessageType as MESSAGES

import re, Timer, asyncio

TIMER_ID_PATTERN = re.compile('^t[1-9]\\d*$')

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
    def setTimer(self, length: 'i', msg: 's') -> 's':
        newId = self.makeId()
        timer = Timer.Timer(length, msg, newId)
        TimerInterface._active_timers[newId] = timer
        timer.setTask(self._loop.create_task(self.executeTimer(timer)))
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
            t = TimerInterface._active_timers[f]
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
        print("Reporting active\n")
        return active

    #removes the timer with the specified id
    @method()
    def removeTimer(self, id: 's') -> 'b':
        return self.clearTimer(id)

    #pauses the timer with the specified id
    @method()
    def pauseTimer(self, id: 's') -> 'bs':
        if id not in TimerInterface._active_timers:
            #errorMsg = "timer %s not found." % id
            raise DBusError(ERRORS.FAILED, 'bok oldu')
            return [False, errorMsg]
        timer: Timer.Timer = TimerInterface._active_timers[id]
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
        timer: Timer.Timer = TimerInterface._active_timers[id]
        if timer.isRunning:
            errorMsg = "timer %s already running." % id
            return [False, errorMsg]
        else:
            remaining = timer.remaining
            timer.end = datetime.now() + timedelta(seconds=remaining)
            timer.setTask(_loop.create_task(executeTimer(remaining)))
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
    async def executeTimer(self, timer):
        await asyncio.sleep(timer)
        await TimerInterface.clearTimer(timer.id)

    async def verifyId(self, id):
        return re.match(TIMER_ID_PATTERN, id)

    def makeId(self) -> str:
        if not TimerInterface._active_timers:
            TimerInterface._ids = 1
            return "t1"
        TimerInterface._ids += 1
        return ("t%i" % TimerInterface._ids)

class TimerInterfaceError(DBusError):

    def __init__(self, text, reply=None):
        super().__init__(ERRORS.FAILED, text, reply=reply)