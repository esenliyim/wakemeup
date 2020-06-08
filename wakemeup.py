import getopt, sys, argparse, time, re, dbus

OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp"
BUS_NAME = "com.esenliyim.WakeMeUp"

def main():
    parser = argparse.ArgumentParser(description="set up a timer or alarm")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--alarm', action='store_true', help='set alarm')
    group.add_argument('-t', '--timer', action='store_true', help='set timer')
    group.add_argument('-s', '--show', action='store_true', help='show active')
    
    parser.add_argument('-m', '--message', type=str, metavar='',
     required=False, help='message to display when the timer goes off')
    parser.add_argument('time', help='how long the timer is gonna go', type=str)

    argus = parser.parse_args()
    timer = argus.time

    if argus.timer:
        plainMins = re.compile('^\\d+$')
        likeHours = re.compile('^\\d+:[0-5]\\d$')

        if plainMins.match(timer):
            timer = int(timer)
        elif likeHours.match(timer):
            timer = getMinutes(timer)
        else:
            print("invalid time input")
            parser.print_help()
        setTimer(timer, argus.message)
        
    elif argus.alarm:
        setAlarm(argus.message, argus.time)
    
    elif argus.show:
        bus = dbus.SessionBus()
        daemon = bus.get_object(BUS_NAME, '/Timer')
        print(daemon.getCount())

def setAlarm(msg, length):
    print("asd")

def setTimer(timer, msg):
    bus = dbus.SessionBus()
    daemon = bus.get_object(BUS_NAME, '/Timer')
    response = daemon.setTimer(timer, msg)
    print(response)

def getMinutes(timeAsString):
    hour, minute = timeAsString.split(':')
    return (60 * int(hour)) + int(minute) 

def printMessage(msg):
    if msg == None:
        return
    else:
        print(msg)

if __name__ == '__main__':
    main()