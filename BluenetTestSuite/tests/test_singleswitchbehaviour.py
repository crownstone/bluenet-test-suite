"""
All tests that concern a single switch behaviour.
"""

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *


def common_setup():
    sendClearBehaviourStoreEvent()
    time.sleep(1) # clearing the store takes a bit more time maybe

    sendSwitchAggregatorReset()

def add_common_setup(scenario):
    scenario.clearTime()
    scenario.addEvent(common_setup)

    scenario.setTime(0,0)

    # behaviour engine resolves to 0 when no behaviours are stored
    scenario.addExpectAny("SwitchAggregator", "behaviourState", ["0","-1"], "behaviourState should've been reset after common init", True)

    # twilight engine resolves to 100 when no behaviours are stored
    scenario.addExpectAny("SwitchAggregator", "twilightState", ["100", "-1"], "twilightState should've been reset after common init")

    # override state is a hasvalue that should be empty after clearing it
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been reset after common init")

    # aggregated state might have been set to -1, or 0 depending on wether updateState has already been called
    scenario.addExpectAny("SwitchAggregator", "aggregatedState", ["0", "-1"], "aggregatedState should've been reset after common init", True)

# ----------------------------------------------------------------------------------------------------------------------
# Definition of the scenarios
# ----------------------------------------------------------------------------------------------------------------------

def build_scenario_0(FW):
    """
    Returns a list of 2-lists: [time, 0ary function] that describes exactly
    what needs to be executed when. The 0ary functions return a falsey value
    when it succeeded, and a string describing what went wrong else.
    """

    def setup_scenario():
        sendBehaviour(0, buildTwilight          ( 9, 12, 80))
        sendBehaviour(1, buildTwilight          (11, 15, 60))
        sendBehaviour(2, buildSwitchBehaviour   (13, 15, 100))
        sendBehaviour(3, buildSwitchBehaviour   (14, 15, 30))

    scenario = TestScenario(FW, "scenario 0")
    add_common_setup(scenario)
    scenario.addEvent(setup_scenario)

    # behaviour 0 becomes active
    scenario.setTime(9, 0)
    scenario.addExpect( "SwitchAggregator", "overrideState", "-1", "overridestate should still be unset")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "0", "aggregatedState should be off as nothing has turned it on")

    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftEvent)

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

    return scenario


def build_scenario_1(FW):
    """
    This scenario tests if a switchcraft induced override with value zero
    will 'mute' a subsequent switching behaviour.

    Returns a list of 2-lists: [time, 0ary function] that describes exactly
    what needs to be executed when. The 0ary functions return a falsey value
    when it succeeded, and a string describing what went wrong else.
    """

    def setup_scenario():
        sendBehaviour(0, buildTwilight          ( 9, 15, 80))
        sendBehaviour(1, buildSwitchBehaviour   (12, 15, 70))

    scenario = TestScenario(FW, "scenario 1")
    add_common_setup(scenario)
    scenario.addEvent(setup_scenario)

    # twilight becomes active
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate shouldn't have changed")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no override or behaviour active")

    # switch craft occurs
    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftEvent)

    scenario.setTime(10, 1)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should be set to translucent after switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "80", "aggregatedState should be equal to twilight value when no active switchbehaviours")

    # switchcraft occurs
    scenario.setTime(11, 0)
    scenario.addEvent(sendSwitchCraftEvent)

    # override state will be set to 0.
    scenario.setTime(11, 1)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate should be cleared after last switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 after last swithcraft")

    # switch behaviour becomes active, this should throw away the override state.
    scenario.setTime(12, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should be cleared after last switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be equal to switchbehaviour value when active twilights don't have lower values")

    return scenario


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

    scenario = TestScenario(FW, "scenario 2")
    add_common_setup(scenario)
    scenario.addEvent(setup_scenario_2)

    # behaviour 0, twilight, becomes active, nothing happens.
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've not have changed when twilight becomes active")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no override or behaviour active")

    # switchcraft occurs
    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftEvent)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should've been set to translucent after switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "80", "aggregatedState should be equal to twilight value when translucent override is set")

    # behaviour 1, switch, becomes active, it has lower intensity so gets used for the agregated state
    scenario.setTime(11, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should've been cleared until all switching behaviours become inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be equal to the minimum of behaviour state and twilight state")

    # switchcraft occurs
    scenario.setTime(12, 0)
    scenario.addEvent(sendSwitchCraftEvent)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate should've been set 0 after switchcraft")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0","aggregatedState should be equal override state when it has a non-translucent value")

    # behaviour 2, switch, becomes active, it has lower intensity so gets used for the agregated state
    scenario.setTime(13, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate shouldn't have been changed when switch behaviour becomes active")
    scenario.addEvent(sendSwitchCraftEvent)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate shouldn't have been changed when switch behaviour becomes active")
    scenario.setTime(13, 1)
    scenario.addExpect("SwitchAggregator", "behaviourState", "30", "behaviour state value incorrectly resolved")
    scenario.addExpect("SwitchAggregator", "twilightState", "80", "twilight state value should be set to the one of the unique twilight behaviour ")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "30", "aggregatedState should be equal to the minimum of behaviour state and twilight state")

    # all behaviours become inactive, override should clear
    scenario.setTime(14, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have been cleared when all switch behaviours become inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no behaviour or override is active")

    # behaviour 3, switch becomes active, as override cleared it should express in the aggregatedstate
    scenario.setTime(15, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate shouldn't have changed when switch behaviour becomes active")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should be equal to behaviour state when it is less than twilight state")

    return scenario


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

    scenario = TestScenario(FW, "scenario 3")
    add_common_setup(scenario)
    scenario.addEvent(setup_scenario_3)

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
    scenario.setTime(12, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been cleared when it is non-zero and all switch behaviours become inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be equal to 0 when no override state or switch behaviours are active")

    return scenario


def build_scenario_4(FW):
    """
    Opaque switch command induces override should be cleared when behaviour turns
    off.
    """

    def setup_scenario():
        sendBehaviour(0,        buildTwilight(9, 12, 70))
        sendBehaviour(1, buildSwitchBehaviour(11, 12, 80))

    scenario = TestScenario(FW, "scenario 4")
    add_common_setup(scenario)
    scenario.addEvent(setup_scenario)

    scenario.setTime(10, 0)
    scenario.addEvent(bind(sendSwitchCommand, 50))
    scenario.addExpect("SwitchAggregator", "overrideState", "50", "overridestate should've been set to last switch command")
    scenario.addExpect("SwitchAggregator", "twilightState", "70", "twilight state value incorrect")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should match the override state")

    scenario.setTime(11, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "50", "overridestate should not change after this switch behaviour becomes active")
    scenario.addExpect("SwitchAggregator", "behaviourState", "80", "behaviour state value incorrect")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should match the override state")

    scenario.setTime(12, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have cleared when behaviour deactivated")
    scenario.addExpect("SwitchAggregator", "twilightState", "100", "twilight state value incorrect")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no override or switch behaviour is active")

    return scenario


def build_scenario_5(FW):
    """
    Opaque switch command induces override should be cleared when behaviour turns
    off.
    """

    def setup_scenario():
        sendBehaviour(0,        buildTwilight(9, 13, 70))
        sendBehaviour(1, buildSwitchBehaviour(9, 13, 100))

    scenario = TestScenario(FW, "scenario 5")
    add_common_setup(scenario)
    scenario.addEvent(setup_scenario)

    # switch behaviour becomes active
    scenario.setTime(9, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "twilightState", "70", "twilight state value incorrect")
    scenario.addExpect("SwitchAggregator", "behaviourState", "100", "behaviour state value incorrect")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be set to twilight value because a switch behaviour is active")

    # switch command occurs
    scenario.setTime(10, 0)
    scenario.addEvent(bind(sendSwitchCommand, 50))
    scenario.addExpect("SwitchAggregator", "overrideState", "50", "overridestate should've been set to switch command value")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "50", "aggregatedState should match the override state")

    # switchcraft occurs
    scenario.setTime(11, 0)
    scenario.addEvent(sendSwitchCraftEvent)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate should be set to 0 when toggling switchcraft in on state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should match the override state")

    # switchcraft occurs
    scenario.setTime(12, 0)
    scenario.addEvent(sendSwitchCraftEvent)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should have been set to translucent when toggling switchcraft in off state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "70", "aggregatedState should be resolved to twilight value as override is translucent")

    # behaviours become inactive
    scenario.setTime(13, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have been cleared when behaviour became inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no switch behaviour or override state is active")

    return scenario


def build_scenario_7(FW):
    """
    Translucent switch commands use resolved behaviour intensity when there are active ones.

    (Will happen when  multiple switchcrafts happen during a behaviour active period).
    """

    def setup_scenario():
        sendBehaviour(0, buildSwitchBehaviour(9, 12, 80))

    scenario = TestScenario(FW, "scenario 7")
    add_common_setup(scenario)
    scenario.addEvent(setup_scenario)

    # switch behaviour becomes active
    scenario.setTime(9, 0)
    # scenario.wait(1)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "behaviourState", "80", "behaviourState incorrect")
    scenario.addExpect("SwitchAggregator", "twilightState", "100", "twilightState incorrect")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "80", "aggregatedState should be set to active switch behaviour value", True)

    # switchcraft occurs
    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftEvent)
    scenario.addExpect("SwitchAggregator", "overrideState", "0", "overridestate should be set to 0 when toggling switchcraft in 'on' state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should match the override state")

    # switchcraft occurs
    scenario.setTime(11, 0)
    scenario.addEvent(sendSwitchCraftEvent)
    scenario.addExpect("SwitchAggregator", "overrideState", "255", "overridestate should have been set to translucent when toggling switchcraft in off state")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "80", "aggregatedState should be resolved to switchbehaviour value as override is translucent")

    # behaviours become inactive
    scenario.setTime(12, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should have been cleared when behaviour became inactive")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should be 0 when no switch behaviour or override state is active")

    return scenario


# ----------------------------------------------------------------------------------------------------------------------
# Definitions of how to run the test
# ----------------------------------------------------------------------------------------------------------------------

def run_all_scenarios(FW):
    fullReset()
    setAllowDimming(True)

    time.sleep(5)

    result = []

    scenarios = [
        build_scenario_0(FW),
        build_scenario_1(FW),
        build_scenario_2(FW),
        build_scenario_3(FW),
        build_scenario_4(FW),
        build_scenario_5(FW),
        build_scenario_7(FW),
    ]

    for scenario in scenarios:
        print("running scenario '{0}'".format(scenario.name))
        result += [scenario.run()]

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
