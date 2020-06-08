# wakemeup

A command line utility for setting up timers and alarms


## Feature goals

`wakemeup <command> [options] <args>`

### command `alarm`:

sets up an alarm for the specified time

#### functional requirements

* figure out if the specified time is today or when

* accept different formats for time input like `14:53` or `2:53 pm` or `1453`

* optional message to go along with the alarm

* do something when the alarm goes of course

### command `timer`:
sets up a timer

`wakemeup timer -m 'time up' 90` to set a 90-minute timer with the message "time up"

`wakemeup timer 1:30` to set a 1 hour 30 minutes timer 

`wakemeup timer 90` to set a 90-minute timer with no message

#### functional requirements:

* default to minutes unless time unit is specified

* optional message to go along with the timer

* do something when timer goes off of course