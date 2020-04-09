"""
All tests that concern a single switch behaviour.
"""

from testframework.framework import *
from testframework.utils import *
from testframework.scenario import *

# ----------------------------------------------------------------------------------------------------------------------
# Definition of the scenarios
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Definitions of how to run the test
# ----------------------------------------------------------------------------------------------------------------------

def run_scenario(eventlist):
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
