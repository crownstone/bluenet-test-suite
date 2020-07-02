"""
When an active behaviour is deleted from the store it might result in a user
being left in the dark if we would not incorporate this into the firmware.

It is okay to change intensity so that a user gets immediate feedback, but
it should not happen that a transition between on/off occurs because of a
change in behaviour configuration.
"""

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *



def clean_setup():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(1)

def load_behaviours():
    """ TODO """
    sendBehaviour(2, buildSwitchBehaviour(13, 15, 100))
    sendBehaviour(3, buildSwitchBehaviour(14, 15, 30))

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

def buildScenarioNoTurnOffOnDelete():
    """
    If the last active behaviour is deleted, there should not be a state change
    """
    pass

def buildScenarioNoTurnOnOnDelete():
    """
    Ok het wordt leuker met die delete behaviour exception:
    stel je hebt een twee behaviours,
    - 09:00-18:00 80%, no presence clause
    - 09:00-12:00 0%, when in room X
    Scenario:
    - het is 11:00, je bent in room X ==> behaviour zegt 0% omdat conflict resolution smalste tijd window pakt.
    - je delete behaviour 2 ==> behaviour zegt nu 80% omdat er nog maar 1 behaviour over is.
    Er gaat een misthoorn aan op 80% tewijl hij net uit stond, je baby wordt wakker, alles gaat mis
    """
    pass


def buildScenarioAllowIntensityChangesOnChange():
    """
    When only the intensity of a behaviour is changed, or a deletion of a behaviour
    results only in an intensity change of the behaviour handler, allow the change to happen.
    """
    pass

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
