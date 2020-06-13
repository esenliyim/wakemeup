from datetime import datetime, timedelta

#the class for timer objects
#length:int is how long they run,
# finalAction:(for now)str is the message to be displayed afterwards
# started:datetime is when the timer was started
# end:datetime is when it's supposed to end
# TODO implement custom actions as finalAction, like running shell commands
class Timer():

    def __init__(self, length: int, id:str, *args, **kwargs):
        self._id = id
        self._initialDuration = length
        self._remaining = length
        self._started = datetime.now()
        self._end = self._started + timedelta(seconds=length)
        self._isRunning = True
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, t):
        self._task = t

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, msg):
        self._message = msg
    
    @property
    def command(self):
        return self._command
    
    @command.setter
    def command(self, cmd):
        self._command = cmd

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id

    @property
    def remaining(self):
        return self._remaining
    
    @remaining.setter
    def remaining(self, r):
        self._remaining = r

    @property
    def started(self):
        return self._started
    
    @started.setter
    def started(self, s):
        self._started = s
    
    @property
    def end(self):
        return self._end
    
    @end.setter
    def end(self, end):
        self._end = end

    @property
    def isRunning(self):
        return self._isRunning

    @isRunning.setter
    def isRunning(self, i):
        self._isRunning = i

    @property
    def initialDuration(self):
        return self._initalDuration

    @initialDuration.setter
    def initialDuration(self, d):
        self._initialDuration = d