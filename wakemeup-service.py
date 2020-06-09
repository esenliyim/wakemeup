import dbus, dbus.service, time, threading
from concurrent.futures import ThreadPoolExecutor
from random import choice
from string import ascii_lowercase

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"

def startTimer(length, msg):
    timer = Timer(length, msg=msg)
    print("set timer for", str(length))
    time.sleep(length)

class WakerUpper(dbus.service.Object):

    def __init__(self):
        self.bus = dbus.SessionBus()
        name = dbus.service.BusName(BUS_NAME, bus=self.bus)
        super().__init__(name, '/Timer')
    
    @dbus.service.method(IFACE, in_signature='is', out_signature='s')
    def setTimer(self, timer, msg):
        f = executor.submit(startTimer, int(timer), msg)
        f._done_callbacks.append(WakerUpper.clearTimer)
        timers.append(f)
        return "done " + str(len(timers))
    
    @dbus.service.method(IFACE, in_signature='', out_signature='i')
    def getTimers(self):
        return len(timers)

    def clearTimer(f):
        timers.remove(f)

class Timer():
    def __init__(self, length, msg=""):
        self.length = length
        self.msg = msg


if __name__ == "__main__":
    import dbus.mainloop.glib
    from gi.repository import GLib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    with ThreadPoolExecutor(max_workers = 5) as executor:
        loop = GLib.MainLoop()
        object = WakerUpper()
        timers = []
        loop.run()