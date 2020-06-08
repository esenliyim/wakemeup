import dbus, dbus.service, time
from concurrent.futures import ThreadPoolExecutor

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"

#executor = ThreadPoolExecutor(max_workers = 10)

def getList():
    return []

def startTimer(length):
    print("set for", length)
    time.sleep(length)
    print("bokbok")

class WakerUpper(dbus.service.Object):

    futures = []

    def __init__(self, list):
        self.bus = dbus.SessionBus()
        name = dbus.service.BusName(BUS_NAME, bus=self.bus)
        super().__init__(name, '/Timer')
    
    @dbus.service.method(IFACE, in_signature='is', out_signature='s')
    def setTimer(self, timer, msg):
        #print("time:", type(int(time)))
        #print("msg:", type(msg))
        futures.append(executor.submit(startTimer, (int(timer))))
        return "done " + str(len(futures))
    
    @dbus.service.method(IFACE, in_signature='', out_signature='i')
    def getCount(self):
        return len(futures)

if __name__ == "__main__":
    import dbus.mainloop.glib
    from gi.repository import GLib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    futures = []
    with ThreadPoolExecutor(max_workers = 5) as executor:
        loop = GLib.MainLoop()
        object = WakerUpper(futures)
        loop.run()
        #futures = []

