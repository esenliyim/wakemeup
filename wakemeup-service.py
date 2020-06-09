import dbus, dbus.service, time, threading
from concurrent.futures import ThreadPoolExecutor
from random import choice
from string import ascii_lowercase

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"

def startTimer(timer):
    length = timer.length
    for i in range(length, 0, -1):
        time.sleep(1)
        timer.length = i

class WakerUpper(dbus.service.Object):

    def __init__(self):
        self.bus = dbus.SessionBus()
        name = dbus.service.BusName(BUS_NAME, bus=self.bus)
        super().__init__(name, '/Timer')
    
    @dbus.service.method(IFACE, in_signature='is', out_signature='s')
    def setTimer(self, length, msg):
        timer = Timer(int(length), msg=msg)
        f = executor.submit(startTimer, timer)
        f._done_callbacks.append(WakerUpper.clearTimer)
        timers[f] = timer
        response = "Started timer for " + str(length) + " seconds. \nWhen it's done:" + str(msg)
        return response
    
    @dbus.service.method(IFACE, in_signature='', out_signature='aa{ss}')
    def getTimers(self):
        active = dbus.Array()
        for f in timers:
            t = timers[f]
            timer = dict()
            timer['remaining'] = str(t.length)
            timer['when_finished'] = t.msg
            active.append(dbus.Dictionary(timer))
        print("Reporting active")
        return active

    @dbus.service.method(IFACE, in_signature='', out_signature='')
    def getAlarms(self):
        print("TODO")

    def clearTimer(f):
        timers.pop(f)

class Timer():
    def __init__(self, length, msg=""):
        self.length = length
        self.msg = msg
    def setFuture(self, future):
        self.future = future


if __name__ == "__main__":
    import dbus.mainloop.glib
    from gi.repository import GLib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    with ThreadPoolExecutor(max_workers = 5) as executor:
        loop = GLib.MainLoop()
        object = WakerUpper()
        timers = dict()
        loop.run()