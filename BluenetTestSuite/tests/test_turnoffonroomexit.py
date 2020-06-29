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
- lead:      setup (B), all scenarios should measure value 50 between events (a)-(c2), else value 80 between (b)-(c2), else 0.
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

# presence handler in firmware will keep messages of devices in its list of
# present devices for 10 seconds. After that the grace period of a behaviour
# will extend this to a per behaviour configurable time.
# The default of the application is 5 minutes. We're reducing that to reduce
# the run time of this test.
#
# We add a little bit of extra time to be certain asynchronicity won't be an issue.
presence_grace_period_sec = 3
presence_handler_time_out_sec = 10
precence_time_out_extra_sec = 2

test_room_id = 1
test_scene_intensity = 50
test_behaviour_intensity = 80


# ----- behaviour store setups -----
def clean_setup():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(1)

def setupA():
    clean_setup()

def setupB():
    clean_setup()

    switchbehaviour = SwitchBehaviour()
    switchbehaviour.setTimeAllday()
    switchbehaviour.setDimPercentage(test_behaviour_intensity)
    switchbehaviour.setPresenceSomebodyInLocations(
               test_room_id, presence_grace_period_sec)

    sendBehaviour(0, switchbehaviour)

def setupC():
    clean_setup()

    switchbehaviour = SwitchBehaviour()
    switchbehaviour.setTimeAllday()
    switchbehaviour.setDimPercentage(0)
    switchbehaviour.setPresenceNobodyInLocations(
                test_room_id, presence_grace_period_sec)

    sendBehaviour(0, switchbehaviour)

# ----- relevant timing events -----
def user_enters():
    pass

def user_exits():
    pass

def wait_for_presence_time_out():
    time.sleep(presence_grace_period_sec +
               presence_handler_time_out_sec +
               precence_time_out_extra_sec)

def set_scene():
    """
    Set scene and receive switch commands is indistinguishable to the firmware.
    """
    sendSwitchCommand(test_scene_intensity)

# ---------------------
# ----- scenarios -----
# ---------------------

# ---- sequence 1) ----
#   a - b - c1 - c2

def scenario_A1(FW):
    scenario = TestScenario(FW, "turn off on room exit A1")
    scenario.addEvent(setupA)
    scenario.wait(1)

    # any time will do, but need to be certain a time is set.
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been reset")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "no behaviours should be active")

    expect_message = "override and aggregated state should equal scene value"
    scenario.addEvent(set_scene)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)


    expect_message = "nothing should change as no behaviours are set"
    scenario.addEvent(user_enters)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)


    scenario.addEvent(user_exits)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)


    scenario.addEvent(wait_for_presence_time_out)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)

    return scenario


def scenario_B1(FW):
    scenario = TestScenario(FW, "turn off on room exit A1")
    scenario.addEvent(setupB)
    scenario.wait(1)

    # any time will do, but need to be certain a time is set.
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been reset")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "no behaviours should be active")

    expect_message = "override and aggregated state should equal scene value"
    scenario.addEvent(set_scene)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)

    expect_message = "presence behaviour is valid but override value has priority"
    scenario.addEvent(user_enters)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)

    expect_message = "presence behaviour still valid because of grace period and presence handler time out"
    scenario.addEvent(user_exits)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)

    expect_message = "presence behaviour became inactive, override should reset"
    scenario.addEvent(wait_for_presence_time_out)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", expect_message)

    return scenario

def scenario_C1(FW):
    scenario = TestScenario(FW, "turn off on room exit A1")
    scenario.addEvent(setupC)
    scenario.wait(1)

    # any time will do, but need to be certain a time is set.
    scenario.setTime(8, 0)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", "overridestate should've been reset")
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", "no behaviours should be active")

    expect_message = "override and aggregated state should equal scene value, "
    expect_message += "behaviourState 0 because of active not-present behaviour"
    scenario.addEvent(set_scene)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "behaviourState", "0", expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)

    expect_message = "presence behaviour is valid but override value has priority, "
    expect_message += "behaviourState 0 because of no active behaviours"
    scenario.addEvent(user_enters)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "behaviourState", "0", expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)

    expect_message = "presence behaviour still valid because of grace period and presence handler time out, "
    expect_message += "behaviourState 0 because of no active behaviours"
    scenario.addEvent(user_exits)
    scenario.addExpect("SwitchAggregator", "overrideState", str(test_scene_intensity), expect_message)
    scenario.addExpect("SwitchAggregator", "behaviourState", "0", expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", str(test_scene_intensity), expect_message)

    expect_message = "presence behaviour became inactive, override should reset, "
    expect_message += "behaviourState 0 because of active not-present behaviour"
    scenario.addEvent(wait_for_presence_time_out)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1", expect_message)
    scenario.addExpect("SwitchAggregator", "behaviourState", "0", expect_message)
    scenario.addExpect("SwitchAggregator", "aggregatedState", "0", expect_message)
# ---- sequence 2) ----

# ---- sequence 3) ----

# ---- sequence 4) ----

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
