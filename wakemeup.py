import getopt, sys, argparse, time, re, dbus, string, datetime

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp.Timer"
BUS_NAME = "com.esenliyim.WakeMeUp"

TIMER_PAT = re.compile('(^([1-9]\\d*)(:[0-5]\\d)?(.[0-5]\\d)?$)|(^[1-9]\\d*s$)')

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--alarm', action='store_true', help='set alarm')
    group.add_argument('-t', '--timer', action='store_true', help='set timer')
    group.add_argument('-s', '--show', action='store_true', help='show active')
    
    group2 = parser.add_mutually_exclusive_group()
    parser.add_argument('-m', '--message', type=str, metavar='MESSAGE',
     required=False, help='message to display when the timer goes off')
    group2.add_argument('-c', '--create', help='The target for the timer or alarm. \
        Alarms can be input in 24h <hh:mm> format or in <hh:mm am|pm>.',
         type=str, metavar='TIME')
    group2.add_argument('-r', '--remove', type=str, metavar='ID',
     required=False, help='cancel the timer with ID')
    #group2.add_argument('-c', '--create', help='create timer')

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    

    if args.timer:
        
        if args.create:
            timer = args.create
            seconds = getSeconds(timer)
            if seconds == None:
                print("Error: Invalid time input.\n")
                print(parser.format_help())
                return
            message = args.message
            if not message:
                message = ""
            print("started for", datetime.timedelta(seconds=seconds))
            setTimer(seconds, message)
        elif args.remove:
            id = args.remove
            result = clearTimer(id)
            if result:
                print("oldu")
            else:
                print("olmadı")
        
    elif args.alarm:
        if timer == None:
            parser.print_help()
            return

        setAlarm(args.message, args.time)
    
    elif args.show:
        bus = dbus.SessionBus()
        daemon = bus.get_object(BUS_NAME, OPATH)
        interface = dbus.Interface(daemon, dbus_interface=IFACE)
        timers = dbus.Array(interface.showTimers())
        if timers:
            for i in timers:
                print("Timer ID:", i['ID'])
                print("     Remaining:", i['remaining'])
                print("     When finished:", i['when_finished'])
        else:
            print("No active timers.")
            

def setAlarm(msg, length):
    print("asd")

def setTimer(timer, msg):
    response = getInterface().setTimer(timer, msg)
    print(response)

def getSeconds(timeAsString):
    m = TIMER_PAT.match(timeAsString)
    
    if not m:
        return None
    elif m.group(5):
        return int(m.group(5).strip(string.ascii_letters))
    elif m.group(3):
        seconds = int(m.group(2)) * 3600
        seconds += int(m.group(3).strip(string.punctuation)) * 60
        if m.group(4):
            seconds += int(m.group(4).strip(string.punctuation))
        return seconds
    elif m.group(4):
        return int(m.group(2)) * 60 + int(m.group(4).strip(string.punctuation))
    else:
        return int(m.group(2))

def clearTimer(id):
    return getInterface().removeTimer(id)

def getInterface():
    bus = dbus.SessionBus()
    daemon = bus.get_object(BUS_NAME, OPATH)
    return dbus.Interface(daemon, dbus_interface=IFACE)

if __name__ == '__main__':
    main()