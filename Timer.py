from datetime import datetime, timedelta

#the class for timer objects
#length:int is how long they run,
# finalAction:(for now)str is the message to be displayed afterwards
# started:datetime is when the timer was started
# end:datetime is when it's supposed to end
# TODO implement custom actions as finalAction, like running shell commands
class Timer():

    def __init__(self, length: int, finalAction, id:str):
        self.id = id
        self.remaining = length
        self.finalAction = finalAction
        self.started = datetime.now()
        self.end = self.started + timedelta(seconds=length)
        self.isRunning = True
    
    def setTask(self, task):
        self.task: asyncio.Task = task
