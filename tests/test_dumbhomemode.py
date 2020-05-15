"""
All tests that concern a single switch behaviour.
"""

from testframework.framework import *
from testframework.scenario import *
from firmwarecontrol.utils import *

# ----------------------------------------------------------------------------------------------------------------------
# Definition of the scenarios
# ----------------------------------------------------------------------------------------------------------------------

def common_setup():
    sendClearSwitchAggregatorOverrideAndAggregatedState()
    sendClearBehaviourStoreEvent()
    time.sleep(1)

    sendBehaviour(0, buildTwilight(9, 12, 80))
    sendBehaviour(1, buildTwilight(11, 15, 60))
    sendBehaviour(2, buildSwitchBehaviour(13, 15, 100))
    sendBehaviour(3, buildSwitchBehaviour(14, 15, 30))

def buildDumbScenario(FW):
    """
    Several behaviours and twilights are set up, the parameter home_is_smart will
    decide wether or not to turn on dumb home mode and expectancies are adjusted accordinginly.
    """
    scenario = TestScenario(FW, "DumbHome")
    scenario.addEvent(common_setup)
    scenario.addEvent(bind(sendCommandDumbMode,True))

    # loops through all hours to check if everything is as dumb at all times.
    for hour in range (24):
        scenario.setTime(hour, 0)

        comment = "nothing should happen in dumb home mode, all states must be empty, aggregated 0"
        scenario.addExpect("SwitchAggregator", "overrideState", "-1", comment)
        scenario.addExpect("SwitchAggregator", "behaviourState", "-1", comment)
        scenario.addExpect("SwitchAggregator", "twilightState", "-1", comment)
        scenario.addExpect("SwitchAggregator", "aggregatedState", "0", comment)

        comment = "when switchcraft happens in dumb mode it should always result in translucent override aggregated to 100"
        scenario.addEvent(sendSwitchCraftEvent)
        scenario.addExpect("SwitchAggregator", "overrideState", "255", comment)
        scenario.addExpect("SwitchAggregator", "behaviourState", "-1", comment)
        scenario.addExpect("SwitchAggregator", "twilightState", "-1", comment)
        scenario.addExpect("SwitchAggregator", "aggregatedState", "100", comment)

        comment = "another switchcraft will result in override 0"
        scenario.addEvent(sendSwitchCraftEvent)
        scenario.addExpect("SwitchAggregator", "overrideState", "0", comment)
        scenario.addExpect("SwitchAggregator", "behaviourState", "-1", comment)
        scenario.addExpect("SwitchAggregator", "twilightState", "-1", comment)
        scenario.addExpect("SwitchAggregator", "aggregatedState", "0", comment)

        comment = "received switch commands should not be executed, not even the translucent one"
        scenario.addEvent(bind(sendSwitchCommand,80))
        scenario.addExpect("SwitchAggregator", "overrideState", "0", comment)
        scenario.addExpect("SwitchAggregator", "aggregatedState", "0", comment)
        scenario.addEvent(bind(sendSwitchCommand, 0xff))
        scenario.addExpect("SwitchAggregator", "overrideState", "0", comment)
        scenario.addExpect("SwitchAggregator", "aggregatedState", "0", comment)

        # clear aggregator for next loop iteration
        scenario.addEvent(sendClearSwitchAggregatorOverrideState)

    return scenario


def buildSmartScenario(FW):
    """
    Several behaviours and twilights are set up  and checked for validity.
    (This is to check if reactivating smart home restores its capabilities).
    """
    scenario = TestScenario(FW, "SmartHome")
    scenario.addEvent(common_setup)

    # scenario.addEvent(bind(sendCommandDumbMode,False))

    # nothing is active yet
    scenario.setTime(8, 0)
    scenario.wait(1)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should've been equal to twilight value")

    # behaviour 0 becomes active
    scenario.setTime(9, 1)
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

# ----------------------------------------------------------------------------------------------------------------------
# Definitions of how to run the test
# ----------------------------------------------------------------------------------------------------------------------

def run_all_scenarios(FW):
    fullReset()
    setAllowDimming(True)

    time.sleep(5)

    result = []

    scenarios = [
        buildSmartScenario(FW),
        buildDumbScenario(FW),
        buildSmartScenario(FW), # run smart home again to check if everything was restored back to normal
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
