import datetime
from time import time
from colorama import Fore, Back, Style

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
        self.name = name
        self.currenttime = None
        self.currentcomment = None
        self.guidstr = ""
        self.verbosity_override = None

    def clearTime(self):
        self.currenttime = None

    def setTime(self, hours, minutes, days=0):
        # days is set to 0 to prevent mishaps due to settime(0) being refused by the firmware.
        self.currenttime = getTime_uint32(hours, minutes, days)

    def setTime_secondssincemidnight(self, ssm):
        self.currenttime = ssm

    def setGuid(self,guidstr):
        self.guidstr = guidstr

    def setComment(self, commentstr):
        """
        Sets the default comment string that is appended to the result of executed events.
        Has effect until clearComment or another setComment overrides the current call.
        """
        self.currentcomment = commentstr

    def clearComment(self):
        self.currentcomment = None

    def getComment(self):
        return "" if self.currentcomment is None else "{0}: {1}".format(self.guidstr, self.currentcomment)

    def setVerbosity(self, verbose):
        self.verbosity_override = verbose

    def clearVerbosity(self):
        self.verbosity_override = None

    def addTimeAndEvent(self, event_time, event_func):
        self.eventlist += [[event_time, event_func]]

    def addEvent(self, event_func):
        """
        event_func must be a 0-argument function that returns None on success and
        a human readible failure message when the event has failed.
        """
        self.addTimeAndEvent(self.currenttime, event_func)

    def wait(self, seconds=0):
        """
        Adds an event that simply sleeps for seconds while running the scenario.
        Can be used to resolve subtle timing issues during testing.
        """
        self.addEvent(bind(time.sleep, seconds))

    def addExpect(self, classname, variablename, expectedvalue, errormessage=None, verbose=False):
        verbose = self.verbosity_override if self.verbosity_override is not None else verbose
        errormessage = self.getComment() if errormessage is None else errormessage
        formattederrormessage = "Line {0}: {1}".format(getLinenumber(1), errormessage)
        self.addEvent(
            bind(expect, self.fw, classname, variablename, expectedvalue, formattederrormessage, verbose)
        )

    def addExpectAny(self, classname, variablename, expectedvalues, errormessage=None, verbose=False):
        verbose = self.verbosity_override if self.verbosity_override is not None else verbose
        errormessage = self.getComment() if errormessage is None else errormessage
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
                    if self.verbosity_override:
                        print("{3}TestSuite setTime: {0} ({1:0>2}:{2:0>2}h). sleeping 1 sec.{4}".format(t, (t // 3600) % 24, (t % 3600) // 60, Fore.LIGHTCYAN_EX, Style.RESET_ALL))
                    setTime_uint32(t)

            if self.verbosity_override:
                print("{0}TestSuite execute event{1}".format(Fore.LIGHTCYAN_EX,Style.RESET_ALL))

            response = evt()

            if response:
                if t is not None:
                    return "{2} (at {0:0>2}:{1:0>2}h)".format((t // 3600) % 24, (t % 3600) // 60, response)
                else:
                    return "{0} (at setup time)".format(response)

            previous_t = t

        return TestFramework.success(self.name)




