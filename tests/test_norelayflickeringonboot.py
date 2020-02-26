import time
import uuid

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType

import datetime


def test_norelayflickeringonboot_loopbody(FW, minimal_relay_half_period_ms):
    """
    Assumes that a state change is reported at the exact moment the relay will be switched.

    Resets the device, then waits for some time to record any state changes. Validates all such
    changes are no closer than [minimal_relay_half_period_ms]
    """
    print("##### setup test_bootloadsflashintooverride_loopbody #####")
    # print("reset firmwarestate recorder")
    FW.clear()

    # print("restart test subject")
    sendCommandToCrownstone(ControlType.RESET, [])

    # print("allow device to reset and startup")
    time.sleep(5)

    # filter relevant history
    relay_history_time_value_pairs = [
        [logentry[0], logentry[4]]
        for logentry in FW.historylist if logentry[2] == "Relay" and logentry[3] == "on"
    ]

    min_time_diff_between_relay_switches = datetime.timedelta(microseconds=minimal_relay_half_period_ms * 1000)

    num_relay_state_changes = len(relay_history_time_value_pairs)
    if num_relay_state_changes < 2:
        # print("too few relay state changes reported during flick test to check period lengths ({0})".format(
        # num_relay_state_changes))
        return TestFramework.success()

    failures = []

    first = relay_history_time_value_pairs[0]
    for second in relay_history_time_value_pairs[1:]:
        if first[1] == second[1]:
            # no state change yet.
            pass
        else:
            state_unchanged_time = second[0] - first[0]
            if state_unchanged_time < min_time_diff_between_relay_switches:
                failures += [TestFramework.failure("found too short relay flick: " + repr(state_unchanged_time))]
            # move to next relay state half-period
            first = second

    return failures if failures else TestFramework.success()


def test_norelayflickeringonboot(FW):
    """
    It's not allowed to see/hear any sudden relay state changes after a reboot.
    """
    print("##### test_bootloadsflashintooverride #####")
    print("override switch state to be sure it is set to fully on, and pause 15 sec to enforce persistence")
    sendCommandToCrownstone(ControlType.SWITCH, [100])

    # need time for persistence of switch state to be pushed.
    time.sleep(15)

    result = []
    for i in range(3):
        result += [test_norelayflickeringonboot_loopbody(FW, 1000)]
    return result


if __name__ == "__main__":
    with TestFramework(test_norelayflickeringonboot) as frame:
        if frame != None:
            print(frame.test_run())
        else:
            print(TestFramework.failure())
