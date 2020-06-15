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

import dbus, dbus.service, time, threading, notify2, logging
import signal, sys
from concurrent.futures import ThreadPoolExecutor
from Timer import Timer
from dbus import DBusException
from datetime import datetime, timedelta

#dbus constants
OPATH = "/com/esenliyim/WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"
TIMER_IFACE = BUS_NAME + ".Timer"

#the dbus interface that handles timers
class TimerInterface(dbus.service.Object):

    _active_timers = dict()
    _completed_timers = []

    # Basic definition of the service. Exported to the session bus.
    # TODO look into systembus
    def __init__(self, loop):
        self.loop = loop
        bus = dbus.SessionBus()
        bus.request_name(BUS_NAME)
        name = dbus.service.BusName(BUS_NAME, bus=bus)
        super().__init__(name, OPATH)
        logger.debug("Starting service: %s" % name.get_name())
    
    # Creates a new Timer object and sends it on its way
    @dbus.service.method(TIMER_IFACE, in_signature='iss', out_signature='s')
    def setTimer(self, length, msg, cmd):
        try:
            newId = self.makeTimerId()
            timer = Timer(length, newId, _message=msg, _command=cmd)
            timer.task = executor.submit(self.startTimer, timer)
            self._active_timers[newId] = timer
            return newId
        except Exception as e:
            raise DBusException(str(e))
    
    # Returns a list of all active timers and their relevant properties
    @dbus.service.method(TIMER_IFACE, in_signature='', out_signature='aa{ss}')
    def showTimers(self):
        active = dbus.Array()
        for f in self._active_timers:
            t = self._active_timers[f]
            timer = dict()
            timer['ID'] = t.id
            if t.isRunning:
                remaining = int((t.end - datetime.now()).total_seconds())
                timer['remaining'] = str(remaining)
            else:
                timer['remaining'] = str(t.remaining)
            timer['isRunning'] = str(t.isRunning)
            if hasattr(t, 'message'):
                timer['message'] = t.message
            if hasattr(t, 'command'):
                timer['command'] = t.command
            active.append(dbus.Dictionary(timer))
        logger.info("Reporting %i active" % len(self._active_timers))
        return active

    # Handles the removal of active timers
    @dbus.service.method(TIMER_IFACE, in_signature='s', out_signature='b')
    def removeTimer(self, id):
        for f in self._active_timers:
            t = self._active_timers[f]
            if t.name == id:
                return clearTimer(f)
        return False

    # Handles the pausing of active timers
    # 1. Cancels the Timer object's future
    # 2. Marks the Timer as paused
    # 3. Marks how much longer the timer was supposed to run 
    @dbus.service.method(TIMER_IFACE, in_signature='s', out_signature='b')
    def pauseTimer(self, id):
        if id not in self._active_timers:
            raise DBusException("no such timer")
        timer: Timer = self._active_timers[id]
        if timer.isRunning:
            if not timer.task.cancel():
                raise DBusException("cannot pause timer?")
            timer.isRunning = False
            remaining = int((timer.end - datetime.now()).total_seconds())
            timer.remaining = remaining
            return True
        else:
            raise DBusException("timer %s is already paused" % id)

    # Handles the resuming of active timers
    # 1. Calculates when the timer is gonna end
    # 2. Replaces the cancelled Future with a new one and starts the countdown
    # 3. Marks the Timer as running 
    @dbus.service.method(TIMER_IFACE, in_signature='s', out_signature='b')
    def resumeTimer(self, id):
        if id not in self._active_timers:
            raise DBusException("no such timer")
        timer: Timer = self._active_timers[id]
        if timer.isRunning:
            raise DBusException("timer %s already running" % id)
        else:
            remaining = timer.remaining
            timer.end = datetime.now() + timedelta(seconds=remaining)
            timer.task = executor.submit(self.startTimer, timer)
            timer.isRunning = True
            return True

    # Does the actual legwork of removing a timer
    # 1. Pops it out of the active timers dict
    # 2. Cancels it if the Timer is being prematurely cancelled
    # 3. GC should take care of the rest. Hopefully TODO test 
    def clearTimer(self, id, done):
        if id in self._active_timers:
            timer = self._active_timers.pop(id)
            if not done:
                timer.task.cancel()
            return True
        else:
            return False
        
    # Creates a new id for the Timer
    # Counts up from "t1". Resets back to t1 when there are no active timers.
    # That means if there are only Timers t3 and t17 are running, and if t17
    # was the last one added, it will return t18. Once all active timers
    # go off and the active_timers list is empty, the names reset to t1. 
    def makeTimerId(self) -> str:
        if not self._active_timers:
            self._ids = 1
            return "t1"
        self._ids += 1
        return "t%i" % self._ids

    # The final destination of the timer.
    # and custom command/script execution 
    def setOffTimer(self, timer: Timer):
        timer.isRunning = False
        timer.restarting = False
        self._completed_timers.append(timer)
        #TODO server_capabilities ???
        if hasattr(timer, 'message'):
            n = notify2.Notification(
                "Time is up!",
                timer.message,
                "dialog-information"
            )
            if not n.actions:
                n.add_action(
                    "dismissed",
                    "Dismiss",
                    self.dismissCallback,
                    timer
                )
                n.add_action(
                   "restarted",
                   "Restart",
                   self.restartCallback,
                   timer
                )
            n.set_timeout(5)
            n.connect('closed', self.closedEvent)
            n.show()

    # the main "body" of the Timer, which is simply waiting until it is time
    # to do something interesting
    def startTimer(self, timer: Timer):
        time.sleep(timer.remaining)
        self.setOffTimer(timer)

    # The dismiss button on the notification. Deletes the timer.
    def dismissCallback(self, n, a, timer=None):
        logger.debug("Dismiss clicked for %s" % timer.id)
        timer.restarting = False

    # TODO implement actual restarting
    def restartCallback(self, n, a, timer=None):
        logger.debug("Restart clicked for %s" % timer.id)
        timer.restarting = True

    def closedEvent(self, n):
        while self._completed_timers:
            timer: Timer = self._completed_timers.pop()
            if timer.restarting:
                timer.initialize()
                timer.task = executor.submit(self.startTimer, timer)
                logger.debug("notification closing with %s restarting" % timer.id)
            else: 
                self.clearTimer(timer.id, True)
                logger.debug("notification closing with %s terminating" % timer.id)


# register SIGINT with sigHandler for graceful ctrl+c and KILL
def sigHandler(sig, frame):
    signal.signal(sig, signal.SIG_IGN)
    print() # only to get rid of the annoying '%' in the terminal
    logger.debug('Killing process.')
    sys.exit(0)
signal.signal(signal.SIGINT, sigHandler)

if __name__ == "__main__":
    import dbus.mainloop.glib
    from gi.repository import GLib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('wmu-service.log')
    fh.setFormatter(logging.Formatter('%(asctime)s:%(module)s:%(message)s'))
    logger.addHandler(fh)
    #TODO pool size??? by default no. of CPU cores * 5
    with ThreadPoolExecutor() as executor:
        notify2.init("wakemeup")
        loop = GLib.MainLoop()
        object = TimerInterface(loop)
        timers = dict()
        logger.info("Starting loop.")
        loop.run()