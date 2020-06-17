from time import time

from BluenetTestSuite.testframework.events import *
from BluenetTestSuite.firmwarecontrol.utils import *

class TestScenario:
    """
    A test scenario consists of expected values or other events to happen/measure at specific times.
    This class makes it easier to build a list of such events through some utility functions and by
    keeping track of a 'current time' so that you don't have to have to retype all the same thing over and over.

    Current time will initially be equal to None, indicating events that should be considered as 'setup' functions.
    """
    def __init__(self, FW, name="TestScenario"):
        self.fw = FW
        self.eventlist = []
        self.currenttime = None
        self.name = name

    def clearTime(self):
        self.currenttime = None

    def setTime(self, hours, minutes, days=0):
        # days is set to 0 to prevent mishaps due to settime(0) being refused by the firmware.
        self.currenttime = getTime_uint32(hours, minutes, days)

    def addTimeAndEvent(self, event_time, event_func):
        self.eventlist += [[event_time, event_func]]

    def addEvent(self, event_func):
        self.addTimeAndEvent(self.currenttime, event_func)

    def wait(self, seconds):
        """
        Adds an event that simply sleeps for seconds while running the scenario.
        Can be used to resolve subtle timing issues during testing.
        """
        self.addEvent(bind(time.sleep, seconds))

    def addExpect(self, classname, variablename, expectedvalue, errormessage="", verbose=False):
        formattederrormessage = "Line {0}: {1}".format(getLinenumber(1), errormessage)
        self.addEvent(
            bind(expect, self.fw, classname, variablename, expectedvalue, formattederrormessage, verbose)
        )

    def addExpectAny(self, classname, variablename, expectedvalues, errormessage="", verbose=False):
        formattederrormessage = "Line {0}: {1}".format(getLinenumber(1), errormessage)
        self.addEvent(
            bind(expectAny, self.fw, classname, variablename, expectedvalues, formattederrormessage, verbose)
        )

    def run(self):
        """
        run the event list in order of the times, skipping forward using a setTime call if necessary.
        eventlist may contain lists with item[0] falsey, in which case the event will be executed before
        any non-falsey time events in the list.

        Note: before each event a command to set the may be issued to the test subject and before
        running the scenario the event list is sorted based on their times. It is therefor tricky
        to run scenarios that test daylight saving time etc.
        """
        previous_t = -1
        for time_event_pair in sorted(self.eventlist, key=lambda items: items[0] if items[0] else -1):
            t = time_event_pair[0]
            evt = time_event_pair[1]

            if t is not None:
                if t != previous_t and t >= 0:
                    setTime_uint32(t)
                    print("setTime called: {0} ({1:0>2}:{2:0>2}h).".format(t, (t // 3600) % 24, (t % 3600) // 60))

            response = evt()

            if response:
                if t is not None:
                    return "{3} at {0:0>2}:{1:0>2}h: {2} ".format((t // 3600) % 24, (t % 3600) // 60, response, self.name)
                else:
                    return "{1} at setup time: {0}".format(response, self.name)

            t = previous_t

        return TestFramework.success(self.name)




