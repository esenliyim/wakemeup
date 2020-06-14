# initial threadpool based implementation of the service
# I moved on to asyncio based implementation but am keeping this
# because why not

import dbus, dbus.service, time, threading, notify2
from concurrent.futures import ThreadPoolExecutor
from Timer import Timer
from dbus import DBusException
from datetime import datetime, timedelta

OPATH = "/com/esenliyim/WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"
IFACE = BUS_NAME + ".Timer"

class TimerInterface(dbus.service.Object):

    _active_timers = dict()

    def __init__(self):
        bus = dbus.SessionBus()
        bus.request_name(BUS_NAME)
        name = dbus.service.BusName(BUS_NAME, bus=bus)
        super().__init__(name, OPATH)
    
    @dbus.service.method(IFACE, in_signature='iss', out_signature='s')
    def setTimer(self, length, msg, cmd):
        try:
            newId = self.makeTimerId()
            timer = Timer(length, newId, _message=msg, _command=cmd)
            timer.task = executor.submit(self.startTimer, timer)
            #f._done_callbacks.append(TimerInterface.clearTimer)
            self._active_timers[newId] = timer
            return newId
        except Exception as e:
            raise DBusException(str(e))
    
    @dbus.service.method(IFACE, in_signature='', out_signature='aa{ss}')
    def showTimers(self):
        active = dbus.Array()
        for f in timers:
            t = timers[f]
            timer = dict()
            timer['ID'] = str(t.name)
            if t.isRunning:
                timer['remaining'] = int((t.end - datetime.now()).total_seconds())
            else:
                timer['remaining'] = t.remaining
            timer['isRunning'] = str(t.isRunning)
            if hasattr(t, 'message'):
                timer['message'] = t.message
            if hasattr(t, 'command'):
                timer['command'] = t.command
            active.append(dbus.Dictionary(timer))
        print("Reporting active")
        return active

    @dbus.service.method(IFACE, in_signature='', out_signature='')
    def getAlarms(self):
        print("TODO")

    @dbus.service.method(IFACE, in_signature='s', out_signature='b')
    def removeTimer(self, id):
        for f in self._active_timers:
            t = self._active_timers[f]
            if t.name == id:
                return clearTimer(f)
        return False

    @dbus.service.method(IFACE, in_signature='s', out_signature='b')
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

    @dbus.service.method(IFACE, in_signature='s', out_signature='b')
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

    def clearTimer(self, id, done):
        if id in self._active_timers:
            timer = self._active_timers.pop(id)
            if not done:
                timer.task.cancel()
            return True
        else:
            return False
        

    def makeTimerId(self) -> str:
        if not self._active_timers:
            self._ids = 1
            return "t1"
        self._active_timers += 1
        return "t%i" % self._ids

    def getById(self, id):
        for f, t in self._active_timers:
            if t.id == id:
                return f, t
        return None

    def setOffTimer(self, timer: Timer):
        if hasattr(timer, 'message'):
            notify2.init("wakemeup", loop)
            n = notify2.Notification(
                "Time is up!",
                timer.message,
                "dialog-information"
            )
            n.add_action(
                "clicked",
                "Dismiss",
                self.bokebok,
                None
            )
            n.set_timeout(notify2.EXPIRES_NEVER)
            n.show()

    def startTimer(self, timer: Timer):
        time.sleep(timer.remaining)
        self.setOffTimer(timer)

    def bokebok(self):
        print("ye")

if __name__ == "__main__":
    import dbus.mainloop.glib
    from gi.repository import GLib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    #TODO pool size??? by default no. of CPU cores * 5
    with ThreadPoolExecutor() as executor:
        loop = GLib.MainLoop()
        object = TimerInterface()
        timers = dict()
        loop.run()