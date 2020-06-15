# wakemeup

A command line utility for setting up timers and alarms. Right now the script "wakemeup" works as a client for "wakemeup-service", communicating over dbus.


## Feature goals

`wmu [-h] (-a | -t | -s) [-c TIME | -d ID | -p ID | -r ID] [-m MESSAGE] [-x COMMAND]`

TODO simplify that mess ^^^

### alarms:

TODO

sets up an alarm for the specified time

#### functional requirements

* accept different formats for time input like `13:14` or `1:14 pm` or `1314`

* optional message to go along with the alarm

* do something when the alarm goes off of course

### timers:

`wakemeup -t -c -m 'time up' 90` to set a 90-minute timer with the message "time up"

`wakemeup -t -c 1:30` to set a 1 hour 30 minutes timer 

`wakemeup -t -c 90` to set a 90-minute timer with no message

#### functional requirements:

* default to minutes unless time unit is specified

* do something when timer goes off of course