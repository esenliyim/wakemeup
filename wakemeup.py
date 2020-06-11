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

# The client script for the timer. I'm planning to make it so
# it can run "offline" without needing a dbus service. Though the client
# allows the timer to run in the background without being bound to a 
# terminal window.

from dbus import DBusException

import getopt, sys, argparse, time, re, dbus, string, datetime


#dbus constants
OPATH = "/com/esenliyim/WakeMeUp"
IFACE = "com.esenliyim.WakeMeUp.Timer"
BUS_NAME = "com.esenliyim.WakeMeUp"

#regex patterns to match arguments against
TIMER_LEN_PAT = re.compile('(^([1-9]\\d*)(:[0-5]\\d)?(.[0-5]\\d)?$)|(^[1-9]\\d*s$)')

def main():
    parser = argparse.ArgumentParser()
    #the main arg group to determine the 'mode of operation'
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--alarm', action='store_true', help='set alarm')
    group.add_argument('-t', '--timer', action='store_true', help='set timer')
    group.add_argument('-s', '--show', action='store_true', help='show active')
    
    #second arg group to further specify what is to be done
    group2 = parser.add_mutually_exclusive_group()
    parser.add_argument('-m', '--message', type=str, metavar='MESSAGE',
     required=False, help='message to display when the timer goes off')
    group2.add_argument('-c', '--create', help='The target for the timer or alarm. \
        Alarms can be input in 24h <hh:mm> format or in <hh:mm am|pm>.',
         type=str, metavar='TIME')
    group2.add_argument('-d', '--delete', type=str, metavar='ID',
     required=False, help='cancel and delete the timer with ID')
    group2.add_argument('-p', '--pause', type=str, metavar='ID',
     help='pause the timer with ID')
    group2.add_argument('-r', '--resume', type=str, metavar='ID', 
     help='resume the timer with ID')

    #this is prettier than the default "no argument found" error
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    #if we're working with timers
    if args.timer:
        
        #if we're creating one
        if args.create:
            #get the specified duration of the timer and convert into seconds
            timer = args.create
            seconds = getSeconds(timer)
            if seconds == None:
                print("Error: Invalid time input.\n")
                parser.print_help()
                return
            #get the message for the timer, default to nothing if nothing given
            message = args.message
            if not message:
                message = ""
            #tell the service to start the timer print the result
            setTimer(seconds, message)
        #if we're removing an existing timer
        elif args.delete:
            id = args.delete
            if id == None:
                print("Error: A valid timer ID must be given.\n")
                parser.print_help()
                return
            if clearTimer(id):
                print("Timer", id, "removed.")
            else:
                print("Timer", id, "could not be removed.")
        elif args.pause:
            id = args.pause
            if not id:
                print("Error: A valid timer ID must be given.\n")
                parser.print_help()
                return
            try:
                print(getInterface().pauseTimer(id))
            except DBusException as e:
                print(e.args[0])
        elif args.resume:
            id = args.resume
            if not id:
                print("Error: A valid timer ID must be given.\n")
                parser.print_help()
                return
            print(getInterface().resumeTimer(id))
    
    #if we're working with alarms
    #COMING SOON
    elif args.alarm:
        if timer == None:
            parser.print_help()
            return

        setAlarm(args.message, args.time)
    
    #if we're just seeing what timers are set
    elif args.show:
        bus = dbus.SessionBus()
        daemon = bus.get_object(BUS_NAME, OPATH)
        interface = dbus.Interface(daemon, dbus_interface=IFACE)
        timers = dbus.Array(interface.showTimers())
        if timers:
            for i in timers:
                print("Timer ID:", i['ID'])
                print("     Remaining:", datetime.timedelta(seconds=int(i['remaining'])))
                print("     When finished:", i['when_finished'])
                print("     Status:", i['isRunning'])
        else:
            print("No active timers.")
            
#not implemented yet
def setAlarm(msg, length):
    print("TODO")

#pass the parameters of the timer to the service, print the response
def setTimer(timer, msg):
    response = getInterface().setTimer(timer, msg)
    print(response)

#verify the time input and convert it to usable seconds
def getSeconds(timeAsString):
    m = TIMER_LEN_PAT.match(timeAsString)
    
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

#tell the service to cancel and remove the specified timer
def clearTimer(id):
    return getInterface().removeTimer(id)

#get a connection to the service
def getInterface():
    bus = dbus.SessionBus()
    daemon = bus.get_object(BUS_NAME, OPATH)
    return dbus.Interface(daemon, dbus_interface=IFACE)

if __name__ == '__main__':
    main()