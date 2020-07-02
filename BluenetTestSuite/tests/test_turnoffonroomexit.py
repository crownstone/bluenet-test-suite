"""
A test that verifies what happens when last user exits the room, and how that interferes with scenes.

Relevant sequencing variations for the events:
a) set scene
b) user enters room
c1) user exits room
c2) presence time out on FW expires

1.  a - b - c1 - c2
2.  b - a - c1 - c2
3.  b - c1 - a - c2
4.  b - c1 - c2 - a  === a

Relevant behaviour store setups:
A) no rules.
B) switchbehaviour: all day, while in room, value 80
C) switchbehaviour: all day, while not in room, value 0

Desire: crownstones with - and without presence based behaviours should react
identically in these sequences. Leading reaction is that of crownstones with presence
based rules enabled.

Solution: add switchbehaviour(while not in room set value 0) to non-presence based crownstones.

Test:
- base line: setup (A), all scenarios should measure override value 50 from the moment event (a) occurs, else value 0.
- lead:      setup (B), all scenarios should measure value 50 between events (a)-(c2), else value 80.
- desire:    setup (C), all scenarios should measure value 50 between events (a)-(c2), else value 0.

Blind spot of test:
No override reset when behaviours go out of scope due to time are tested. (Possible to do, but would add an extra sequence event)
"""

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *

# ----------------------------------------------------------------------------------------------------------------------
# Definition of the scenarios
# ----------------------------------------------------------------------------------------------------------------------

def clean_setup():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(1)

def load_behaviours():
    """ TODO """
    sendBehaviour(2, buildSwitchBehaviour(13, 15, 100))
    sendBehaviour(3, buildSwitchBehaviour(14, 15, 30))

def set_scene():
    """
    Set scene and receive switch commands is indistinguishable to the firmware.
    """
    sendSwitchCommand(50)

def buildScenario(FW):
    """ TODO """
    scenario = TestScenario(FW, "Last user leaves room")
    # scenario.addEvent(clean_setup)
    # scenario.addEvent(load_behaviours)
    #
    # scenario.wait(1)
    # scenario.setTime(8, 0)
    #
    # scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been set to translucent")
    # scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "aggregatedState should've been equal to twilight value")

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
        buildScenario(FW),
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
