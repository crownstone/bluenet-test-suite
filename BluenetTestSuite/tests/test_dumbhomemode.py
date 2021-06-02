"""
All tests that concern a single switch behaviour.
"""

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *

# ----------------------------------------------------------------------------------------------------------------------
# Definition of the scenarios
# ----------------------------------------------------------------------------------------------------------------------

def common_setup():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(5)

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

    scenario.wait(1)
    scenario.addExpect("BehaviourHandler", "isActive", "False" ,"behaviour handler should be inactive when dumb")
    scenario.addExpect("TwilightHandler", "isActive", "False", "twilight handler should be inactive when dumb")

    # loops through all hours to check if everything is as dumb at all times.
    for hour in range (0,24,3):
        scenario.setTime(hour, 0)

        scenario.setComment("nothing should happen in dumb home mode, all states must be empty, aggregated 0 or possibly -1")
        scenario.addExpect("SwitchAggregator", "overrideState", "-1")
        scenario.addExpect("SwitchAggregator", "behaviourState", "-1")
        scenario.addExpect("SwitchAggregator", "twilightState", "-1")
        scenario.addExpectAny("SwitchAggregator", "aggregatedState", ["0", "-1"])

        scenario.setComment("when switchcraft happens in dumb mode it should always result in translucent override aggregated to 100")
        scenario.addEvent(sendSwitchCraftEvent)
        scenario.addExpect("SwitchAggregator", "overrideState", "255")
        scenario.addExpect("SwitchAggregator", "behaviourState", "-1")
        scenario.addExpect("SwitchAggregator", "twilightState", "-1")
        scenario.addExpect("SwitchAggregator", "aggregatedState", "100")

        scenario.setComment("another switchcraft will result in override 0")
        scenario.addEvent(sendSwitchCraftEvent)
        scenario.addExpect("SwitchAggregator", "overrideState", "0")
        scenario.addExpect("SwitchAggregator", "behaviourState", "-1")
        scenario.addExpect("SwitchAggregator", "twilightState", "-1")
        scenario.addExpect("SwitchAggregator", "aggregatedState", "0")

        scenario.setComment("received switch commands should still be executed")
        scenario.addEvent(bind(sendSwitchCommand,80))
        scenario.addExpect("SwitchAggregator", "overrideState", "80")
        scenario.addExpect("SwitchAggregator", "aggregatedState", "80")
        scenario.addEvent(bind(sendSwitchCommand, 0xff))
        scenario.addExpect("SwitchAggregator", "overrideState", "255")
        # aggregated state depends on time...

        # clear aggregator for next loop iteration
        scenario.addEvent(sendSwitchAggregatorReset)

    return scenario


def buildSmartScenario(FW):
    """
    Several behaviours and twilights are set up  and checked for validity.
    (This is to check if reactivating smart home restores its capabilities).
    """
    scenario = TestScenario(FW, "SmartHome")
    scenario.addEvent(common_setup)
    scenario.addEvent(bind(sendCommandDumbMode, False))

    scenario.wait(1)
    scenario.addExpect("BehaviourHandler", "isActive", "True", "behaviour handler should be active when smart")
    scenario.addExpect("TwilightHandler", "isActive", "True", "twilight handler should be active when smart")

    # nothing is active yet
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should've been equal to twilight value")

    # behaviour 0 becomes active
    scenario.setTime(9, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "-1", "overridestate should still be unset")
    scenario.addExpect( "SwitchAggregator", "aggregatedState", "0", "aggregatedState should be off as nothing has turned it on")

    scenario.setTime(10, 0)
    scenario.addEvent(sendSwitchCraftEvent)

    scenario.setTime(10, 1)
    scenario.addExpect( "SwitchAggregator", "overrideState", "255","overridestate should've been set to translucent after switchcraft")
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
        buildSmartScenario(FW),  # run smart home again to check if everything was restored back to normal
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
