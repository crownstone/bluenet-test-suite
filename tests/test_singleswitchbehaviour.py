"""
All tests that concern a single switch behaviour.
"""

import time

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType
from BluenetLib.lib.packets.behaviour.Behaviour import *


# ----------------------------------------------------------------------------------------------------------------------
# Preliminary definitions
# ----------------------------------------------------------------------------------------------------------------------

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

def getTime_uint32(hours, minutes, day=None):
    # day != 0  && (hours != 0 || minutes != 0): sunday
    # epoch is on a thursday, so we add 3*24*60*60 seconds
    return (3 + day if day else 0) * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60

def setTime_uint32(time_as_uint32):
    sendCommandToCrownstone(ControlType.SET_TIME,
                            Conversion.uint32_to_uint8_array(time_as_uint32))
    sleepAfterUartCommand()

def setTime_hmd(hours, minutes, day=None):
    setTime(getTime_uint32(hours,
                           minutes,
                           day if day else 0))


def sendBehaviour(index, behaviour):
    packet = behaviour.getPacket()
    sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [index] + behaviour.getPacket())
    sleepAfterUartCommand()


def setAllowDimming(value):
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1])
    sleepAfterUartCommand()


def sendSwitchCommand(intensity):
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    sleepAfterUartCommand()


def sendClearSwitchAggregatorOverride():
    sendSwitchCommand(0xfe)
    sleepAfterUartCommand()


def sendSwitchCraftCommand():
    sendEventToCrownstone(0x100 + 20 + 2, [])
    sleepAfterUartCommand()


def sendClearBehaviourStoreEvent():
    sendEventToCrownstone(0x100 + 170 + 6, [])
    sleepAfterUartCommand()

# ----------------------------------------------------------------------------------------------------------------------
# General test framework utilities
# ----------------------------------------------------------------------------------------------------------------------

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
    else:
        print("expectation correct: {0}.{1} == {2} ({3})".format(
            classname, variablename, expectedvalue, errormessage))

    return None


# an event is a method taking no arguments that returns a value which is non-Falsey only when it fails.
# it comes with a time at which it should fire.
# the test will sort the event times and execute them until the first returns a non-Falsey value
# when that happens, it considers the scenario failed and reports back the returned value.

def bind(func, *args):
    """
    Returns a nullary function that calls func with the given arguments.
    """
    def noarg_func():
        return func(*args)
    return noarg_func

# ----------------------------------------------------------------------------------------------------------------------
# Definition of the scenarios
# ----------------------------------------------------------------------------------------------------------------------


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


def build_scenario_0(FW):
    """
    Returns a list of 2-lists: [time, 0ary function] that describes exactly
    what needs to be executed when. The 0ary functions return a falsey value
    when it succeeded, and a string describing what went wrong else.
    """

    def setup_scenario_0():
        sendBehaviour(0, buildTwilight          ( 9, 12, 80))
        sendBehaviour(1, buildTwilight          (11, 15, 60))
        sendBehaviour(2, buildSwitchBehaviour   (13, 15, 100))
        sendBehaviour(3, buildSwitchBehaviour   (14, 15, 30))

    scenario = TestScenario(FW)
    scenario.addEvent(setup_scenario_0)

    # nothing is active yet
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should've been equal to twilight value")

    # behaviour 0 becomes active
    scenario.setTime(9, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "-1", "overridestate should still be unset")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "0", "aggregatedState should be off as nothing has turned it on")

    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftCommand)

    scenario.setTime(10, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "255", "overridestate should've been set to translucent after switchcraft")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "80", "aggregatedState should've been equal to twilight value after switchcraft")

    # behaviour 1 becomes active
    scenario.setTime(11, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "255", "overridestate should've been set to translucent after switchcraft")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "60", "aggregatedState should've been equal to twilight value because of conflict resolution")

    # behaviour 2 becomes active
    scenario.setTime(13, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "255", "overridestate should still be set to translucent after switchcraft, reset happens when behaviour falls is cleared")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "60", "aggregatedState should still been equal to conflict resolved twilight value as behaviour has higher intensity value")

    # behaviour 3 becomes active
    scenario.setTime(14, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "255", "overridestate should still be set to translucent after switchcraft, reset happens when behaviour falls is cleared")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "30", "aggregatedState should still been equal to conflict resolved switchbehaviour value as it has lower intensity value")

    # all behaviours become inactive
    scenario.setTime(15, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "-1", "overridestate should've been reset after state match")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "0", "aggregatedState should've been set to 0")

    return scenario.eventlist

def build_scenario_1(FW):
    """
    This scenario tests if a switchcraft induced override with value zero
    will 'mute' a subsequent switching behaviour.

    Returns a list of 2-lists: [time, 0ary function] that describes exactly
    what needs to be executed when. The 0ary functions return a falsey value
    when it succeeded, and a string describing what went wrong else.
    """

    def setup_scenario_1():
        sendBehaviour(0, buildTwilight          ( 9, 15, 80))
        sendBehaviour(1, buildSwitchBehaviour   (12, 15, 70))

    scenario = TestScenario(FW)
    scenario.addEvent(setup_scenario_1)

    # before any behaviour kicks in
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been cleared before running scenario")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no override or behaviour active")

    # twilight becomes active
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate shouldn't have changed")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no override or behaviour active")

    # switch craft occurs
    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftCommand)

    scenario.setTime(10, 1)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should be set to translucent after switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "80", "aggregatedState should be equal to twilight value when no active switchbehaviours")

    # switchcraft occurs
    scenario.setTime(11, 0)
    scenario.addEvent(sendSwitchCraftCommand)

    scenario.setTime(11, 1)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should be cleared after last switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be equal to twilight value when no active switchbehaviours")

    # switch behaviour becomes active
    scenario.setTime(12, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should be cleared after last switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be equal to switchbehaviour value when active twilights don't have lower values")

    return scenario.eventlist

def build_scenario_2(FW):
    """
    This scenario tests if a switchcraft induced override with value 0 is cleared
    when all switching behaviours become inactive.

    It is crucial that the switchcraft event takes place when a switching behaviour
    is active - otherwise the zero override will not clear when they become inactive
    (by design). (This distinguishes it from scenario 1.)

    Returns a list of 2-lists: [time, 0ary function] that describes exactly
    what needs to be executed when. The 0ary functions return a falsey value
    when it succeeded, and a string describing what went wrong else.
    """

    def setup_scenario_2():
        sendBehaviour(0, buildTwilight          ( 9, 16, 80))
        sendBehaviour(1, buildSwitchBehaviour   (11, 14, 70))
        sendBehaviour(2, buildSwitchBehaviour   (13, 14, 30))
        sendBehaviour(3, buildSwitchBehaviour   (15, 16, 50))

    scenario = TestScenario(FW)
    scenario.addEvent(setup_scenario_2)

    # before any behaviour kicks in
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been cleared before running scenario")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no override or behaviour active")

    # behaviour 0, twilight, becomes active, nothing happens.
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've not have changed when twilight becomes active")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no override or behaviour active")

    # switchcraft occurs
    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftCommand)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should've been set to translucent after switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "80", "aggregatedState should be equal to twilight value when translucent override is set")

    # behaviour 1, switch, becomes active, it has lower intensity so gets used for the agregated state
    scenario.setTime(11, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "ff", "overridestate should've been cleared until all switching behaviours become inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be equal to the minimum of behaviour state and twilight state")

    # switchcraft occurs
    scenario.setTime(12, 0)
    scenario.addEvent(sendSwitchCraftCommand)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate should've been set 0 after switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0","aggregatedState should be equal override state when it has a non-translucent value")

    # behaviour 2, switch, becomes active, it has lower intensity so gets used for the agregated state
    scenario.setTime(13, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate shouldn't have been changed when switch behaviour becomes active")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "30", "aggregatedState should be equal to the minimum of behaviour state and twilight state")

    # all behaviours become inactive, override should clear
    scenario.setTime(14, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have been cleared when all switch behaviours become inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no behaviour or override is active")

    # behaviour 3, switch becomes active, as override cleared it should express in the aggregatedstate
    scenario.setTime(15, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate shouldn't have changed when switch behaviour becomes active")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should be equal to behaviour state when it is less than twilight state")

    return scenario.eventlist

def build_scenario_3(FW):
    """
    Tests if override is cleared when all switch behaviours go out of scope.
    And tests switch command with opaque value.

    Returns a list of 2-lists: [time, 0ary function] that describes exactly
    what needs to be executed when. The 0ary functions return a falsey value
    when it succeeded, and a string describing what went wrong else.
    """

    def setup_scenario_3():
        sendBehaviour(0,        buildTwilight(9, 14, 80))
        sendBehaviour(1, buildSwitchBehaviour(9, 12, 70))

    scenario = TestScenario(FW)
    scenario.addEvent(setup_scenario_3)

    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no behaviours are active, nor override exists")

    # behaviours both become active
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be equal to minimum of active behaviour and twilight")

    # switch command occurs
    scenario.setTime(10, 0)
    scenario.addEvent(bind(sendSwitchCommand, 50))
    scenario.addExpect("SwitchAggregator", "overrideState", "50", "overridestate should've been set to translucent")

    scenario.setTime(10, 0)
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should be equal to override state when it is opaque")

    # all behaviours become inactive
    scenario.setTime(11, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been cleared when it is non-zero and all switch behaviours become inactive")

    scenario.setTime(11, 0)
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be equal to 0 when no override state or switch behaviours are active")

    return scenario.eventlist

def build_scenario_4(FW):
    """
    Opaque switch command induces override should be cleared when behaviour turns
    off.
    """

    def setup_scenario():
        sendBehaviour(0,        buildTwilight(9, 12, 70))
        sendBehaviour(1, buildSwitchBehaviour(10, 11, 80))

    scenario = TestScenario(FW)
    scenario.addEvent(setup_scenario)

    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no behaviours are active, nor override exists")

    scenario.setTime(10, 0)
    scenario.addEvent(bind(sendSwitchCommand, 50))
    scenario.addExpect("SwitchAggregator", "overrideState", "50", "overridestate should've been set to last switch command")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should match the override state")

    scenario.setTime(11, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "50", "overridestate should not change after this switch behaviour becomes active")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should match the override state")

    scenario.setTime(12, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have cleared when behaviour deactivated")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should be 0 when no override or switch behaviour is active")

    return scenario.eventlist


def build_scenario_5(FW):
    """
    Opaque switch command induces override should be cleared when behaviour turns
    off.
    """

    def setup_scenario():
        sendBehaviour(0,        buildTwilight(9, 13, 70))
        sendBehaviour(1, buildSwitchBehaviour(9, 13, 100))

    scenario = TestScenario(FW)
    scenario.addEvent(setup_scenario)

    # blank canvas
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no behaviours are active, nor override exists")

    # switch behaviour becomes active
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70",
                       "aggregatedState should be set to twilight value (70) because a switch behaviour(100) is active")

    # switch command occurs
    scenario.setTime(10, 0)
    scenario.addEvent(bind(sendSwitchCommand, 50))
    scenario.addExpect("SwitchAggregator", "overrideState", "50", "overridestate should've been set to switch command value")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should match the override state")

    # switchcraft occurs
    scenario.setTime(11, 0)
    scenario.addEvent(sendSwitchCraftCommand)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate should be set to 0 when toggling switchcraft in on state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should match the override state")

    # switchcraft occurs
    scenario.setTime(12, 0)
    scenario.addEvent(sendSwitchCraftCommand)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should have been set to translucent when toggling switchcraft in off state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be resolved to twilight value as override is translucent")

    # behaviours become inactive
    scenario.setTime(13, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have been cleared when behaviour became inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no switch behaviour or override state is active")

    return scenario.eventlist


def build_scenario_7(FW):
    """
    Translucent switch commands use resolved behaviour intensity when there are active ones.

    (Will happen when  multiple switchcrafts happen during a behaviour active period).
    """

    def setup_scenario():
        sendBehaviour(0, buildSwitchBehaviour(9, 12, 80))

    scenario = TestScenario(FW)
    scenario.addEvent(setup_scenario)

    # blank canvas
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no behaviours are active, nor override exists")

    # switch behaviour becomes active
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "80", "aggregatedState should be set to active switch behaviour value")

    # switchcraft occurs
    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftCommand)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate should be set to 0 when toggling switchcraft in 'on' state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should match the override state")

    # switchcraft occurs
    scenario.setTime(11, 0)
    scenario.addEvent(sendSwitchCraftCommand)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should have been set to translucent when toggling switchcraft in off state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be resolved to switchbehaviour value as override is translucent")

    # behaviours become inactive
    scenario.setTime(12, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have been cleared when behaviour became inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no switch behaviour or override state is active")

    return scenario.eventlist


# ----------------------------------------------------------------------------------------------------------------------
# Definitions of how to run the test
# ----------------------------------------------------------------------------------------------------------------------

def run_scenario( eventlist):
    """
    run the event list in order of the times, skipping forward using a setTime call if necessary.
    eventlist may contain lists with item[0] falsey, in which case the event will be executed before
    any non-falsey time events in the list.
    """
    previous_t = -1
    for time_event_pair in sorted(eventlist, key=lambda items: items[0] if items[0] else -1):
        t = time_event_pair[0]
        evt = time_event_pair[1]

        if t is not None:
            if t != previous_t and t >= 0:
                setTime_uint32(t)

        response = evt()

        if response:
            if t is not None:
                return "{0}:{1}h: {2} ".format(t//3600, (t%3600)//60, response)
            else:
                return "at setup time: {0}".format(response)

        t = previous_t

    return TestFramework.success()


def run_all_scenarios(FW):
    fullReset()
    setAllowDimming(True)

    time.sleep(5)

    result = []

    scenarios = [
        ["0", build_scenario_0(FW)],
        ["1", build_scenario_1(FW)],
        ["2", build_scenario_2(FW)],
        ["3", build_scenario_3(FW)],
        ["4", build_scenario_4(FW)],
        ["5", build_scenario_5(FW)],
        ["7", build_scenario_7(FW)],
    ]

    for scenariodescription in scenarios:
        sendClearSwitchAggregatorOverride()
        sendClearBehaviourStoreEvent()

        print("running scenario '{0}'".format(scenariodescription[0]))

        time.sleep(1)

        result += [run_scenario(scenariodescription[1])]

    return result


if __name__ == "__main__":
    with TestFramework(run_all_scenarios) as framework:
        if framework is not None:
            results = framework.test_run()
            prettyprinter = pprint.PrettyPrinter(indent=4)
            print ("Test finished with result:")
            for result in results:
                print(result)
        else:
            print(TestFramework.failure("Couldn't setup test framework"))
            print("remember, this test assumes behaviour store is clean before running")
