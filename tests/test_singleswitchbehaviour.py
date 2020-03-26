"""
All tests that concern a single switch behaviour.
"""

import time

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType
from BluenetLib.lib.packets.behaviour.Behaviour import *


def buildSwitchBehaviour(from_hours, to_hours, intensity):
    switchbehaviour = Behaviour()
    switchbehaviour.setTimeFrom(from_hours % 24, 0)
    switchbehaviour.setTimeTo(to_hours % 24, 0)
    switchbehaviour.setDimPercentage(intensity)
    return switchbehaviour


def buildTwilight(from_hours, to_hours, intensity):
    twilight = Twilight()
    twilight.setTimeFrom(from_hours % 24, 0)
    twilight.setTimeTo(to_hours % 24, 0)
    twilight.setDimPercentage(intensity)
    return twilight


def sleepAfterUartCommand():
    time.sleep(0.5)


def fullReset():
    print("Resetting crownstone and waiting for dimmer to have started for a cleaner test.")
    sendCommandToCrownstone(ControlType.RESET, [])
    for t in reversed(range(7)):
        print("sleeping for {0} more seconds".format((t + 1) * 10))
        time.sleep(10)

def getTime_uint32(hours, minutes, day=0):
    # day != 0  && (hours != 0 || minutes != 0): sunday
    # epoch is on a thursday, so we add 3*24*60*60 seconds
    return (3 + day) * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60

def setTime_uint32(time_as_uint32):
    sendCommandToCrownstone(ControlType.SET_TIME,
                            Conversion.uint32_to_uint8_array(time_as_uint32))
    SleepAfterUartCommand()

def setTime_hmd(hours, minutes, day=0):
    setTime(getTime_uint32(hours,minutes,day))


def sendBehaviour(index, behaviour):
    packet = behaviour.getPacket()
    sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [index] + behaviour.getPacket())
    SleepAfterUartCommand()


def setAllowDimming(value):
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1])
    SleepAfterUartCommand()


def sendSwitchCommand(intensity):
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    SleepAfterUartCommand()


def sendClearSwitchAggregatorOverride():
    sendSwitchCommand(0xfe)
    SleepAfterUartCommand()


def sendSwitchCraftCommand():
    sendEventToCrownstone(0x100 + 20 + 2, [])
    SleepAfterUartCommand()


def sendClearBehaviourStoreEvent():
    sendEventToCrownstone(0x100 + 170 + 6, [])
    SleepAfterUartCommand()


def expect(FW, classname, variablename, expectedvalue, errormessage=""):
    """
    Checks if the expected value in FW.
    Returns TestFramework failure message when there is one, else None.
    """
    failures = FW.assertFindFailures(classname, variablename, expectedvalue)
    if failures:
        actualvalue = None
        try:
            actualvalue = FW.statedict[failures[0]].get(variablename)
        except:
            actualvalue = "<not found>"

        failmsg = TestFramework.failure("{4}: Expected {0}.{1} to have value {2}, got {3}".format(
            classname, variablename, expectedvalue, actualvalue, errormessage))
        FW.print()
        return failmsg

    return None


# an event is a method taking no arguments that returns a value which is non-Falsey only when it fails.
# it comes with a time at which it should fire.
# the test will sort the event times and execute them until the first returns a non-Falsey value
# when that happens, it considers the scenario failed and reports back the returned value.

def bind(func,*args):
    """
    Returns a nullary function that calls func with the given arguments.
    """
    def noarg_func():
        return func(*args)
    return noarg_func


def test_scenario_0(FW):
    print("##### test scenario 0 #####")

    # setup the
    sendBehaviour(0, buildTwilight          ( 9, 12, 80))
    sendBehaviour(0, buildTwilight          (11, 15, 80))
    sendBehaviour(0, buildSwitchBehaviour   (13, 15, 80))
    sendBehaviour(0, buildSwitchBehaviour   (14, 15, 80))

    # a list of 2-tuples, containing a timestamp and a 0-ary 'evennt' method
    events = [
        [getTime_uint32(9, 0), bind(expect, "SwitchAggregator", "overrideState", "-1",
                                            "Overridestate should've been set to translucent")],

        [getTime_uint32(9, 0), bind(expect, "SwitchAggregator", "aggregatedState", "0",
                                            "Overridestate should've been equal to twilight value")],

        [getTime_uint32(10, 0), sendSwitchCraftCommand],

        [getTime_uint32(10, 1), bind(expect, "SwitchAggregator", "overrideState", "255",
                                             "Overridestate should've been set to translucent")],

        [getTime_uint32(10, 1), bind(expect, "SwitchAggregator", "aggregatedState", "80",
                                             "Overridestate should've been equal to twilight value")],

        [getTime_uint32(11, 1), bind(expect, "SwitchAggregator", "overrideState", "255",
                                             "Overridestate should've been set to translucent")],

        [getTime_uint32(11, 1), bind(expect, "SwitchAggregator", "aggregatedState", "80",
                                             "Overridestate should've been equal to twilight value")]
    ]

    # run the event list in order of the times, skipping forward using a setTime call each event
    for i in sorted(events, key=lambda items: items[0]):
        t = i[0]
        evt = i[1]

        setTime_uint32(t)
        response = evt()
        if response:
            return response

    return TestFramework.success()




def test_method(FW):
    fullReset()
    setAllowDimming(True)
    sendClearSwitchAggregatorOverride()
    sendClearBehaviourStoreEvent()

    time.sleep(5)

    result = []
    scenarios = [test_scenario_0]

    for scenario in scenarios:
        result += [scenario(FW)]

    return result


if __name__ == "__main__":
    with TestFramework(test_method) as frame:
        if frame != None:
            results = frame.test_run()
            prettyprinter = pprint.PrettyPrinter(indent=4)
            print ("Test finished with result:")
            for result in results:
                print(result)

        else:
            print(TestFramework.failure("Couldn't setup test framework"))
            print("remember, this test assumes behaviour store is clean before running")
