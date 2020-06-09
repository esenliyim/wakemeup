import getopt, sys, argparse, time, re, dbus, string

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"

TIMER_PAT = re.compile('(^([1-9]\\d*)(:[0-5]\\d)?(.[0-5]\\d)?$)|(^[1-9]\\d*s$)')

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--alarm', action='store_true', help='set alarm')
    group.add_argument('-t', '--timer', action='store_true', help='set timer')
    group.add_argument('-s', '--show', action='store_true', help='show active')
    
    parser.add_argument('-m', '--message', type=str, metavar='MESSAGE',
     required=False, help='message to display when the timer goes off')
    parser.add_argument('time', help='The target for the timer or alarm. \
        Alarms can be input in 24h <hh:mm> format or in <hh:mm am|pm>.',
     nargs='?', type=str)

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    timer = args.time

    if args.timer:
        if timer == None:
            parser.print_help()
            return
        
        seconds = getSeconds(timer)

        if seconds == None:
            print("Error: Invalid time input.\n")
            print(parser.format_help())
            return

        print("setting for:", str(seconds), "seconds")
        message = args.message
        if message:
            print("msg:", message)
        #setTimer(timer, args.message)
        
    elif args.alarm:
        if timer == None:
            parser.print_help()
            return

        setAlarm(args.message, args.time)
    
    elif args.show:
        bus = dbus.SessionBus()
        daemon = bus.get_object(BUS_NAME, '/Timer')
        print(daemon.getTimers())

def setAlarm(msg, length):
    print("asd")

def setTimer(timer, msg):
    bus = dbus.SessionBus()
    daemon = bus.get_object(BUS_NAME, '/Timer')
    response = daemon.setTimer(timer, msg)
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

def printMessage(msg):
    if msg == None:
        return
    else:
        print(msg)

if __name__ == '__main__':
    main()