from testframework.events import *
from firmwarecontrol.utils import *

class TestScenario:
    """
    Builder class for scenarios, as there are many of those things we build.

    You can add expected values or other events to happen/measure at specific times.

    Keeps track of a 'current time' which is initially None so that you don't have to
    have to retype all the same thing over and over.

    clearing current time (or setting it to None) will allow you to add 'setup' functions
    to the event list.
    """
    def __init__(self, FW):
        self.fw = FW
        self.eventlist = []
        self.currenttime = None

    def clearTime(self):
        self.currenttime = None

    def setTime(self, hours, minutes, days=None):
        self.currenttime = getTime_uint32(minutes, hours, days)

    def addTimeAndEvent(self, event_time, event_func):
        self.eventlist += [[event_time, event_func]]

    def addEvent(self, event_func):
        self.addTimeAndEvent(self.currenttime, event_func)

    def addExpect(self, classname, variablename, expectedvalue, errormessage=""):
        self.addEvent(
            bind(expect, self.fw, classname, variablename, expectedvalue, errormessage)
        )



