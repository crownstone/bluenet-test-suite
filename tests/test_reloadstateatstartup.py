# === off at boot ===
# 	boot: flash state = 0, board = ACR01B10C
# relay = 0
# override state = 0
# 	dimmer power timeout
#
#
#
# === on at boot ===
# 	boot: flash state = 128, board = ACR01B10C
# relay = 1
# override state = 100
# 	dimmer power timeout

import time
import uuid

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType


def test_bootloadsflashintooverride_loopbody(FW, intensity):
    print("##### setup test_bootloadsflashintooverride_loopbody (intensity: {0}) #####".format(intensity))

    # override switch state
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])

    # need time for persistence of switch state to be pushed.
    time.sleep(15)

    # print("reset firmwarestate recorder")
    FW.clear()

    # print("restart test subject")
    sendCommandToCrownstone(ControlType.RESET, [])

    # print("allow device to reset and startup")
    time.sleep(10)

    # Test SwitchAggregator overrideState
    expected_override_state = min(max(0, intensity), 100)
    if FW.assertFindFailures("SwitchAggregator", 'overrideState', expected_override_state):
        failureid = uuid.uuid4()
        print("----- Failure: {0} -----".format(failureid))
        FW.print()
        return TestFramework.failure("{0} overrideState should've been {1} after reset".format(
                failureid, expected_override_state))

    # Test HwSwitch.relay state
    expected_relay_state = bool((intensity >> 7) & 1)
    if FW.assertFindFailures("HwSwitch", 'relay', expected_relay_state):
        failureid = uuid.uuid4()
        print("----- Failure: {0} -----".format(failureid))
        return TestFramework.failure("{0} relaystate should've been {1} after reset".format(
                failureid, expected_relay_state))

    return TestFramework.success()


def test_bootloadsflashintooverride(FW):
    result = []
    for intensity in [0, 128]:
        result += [test_bootloadsflashintooverride_loopbody(FW, intensity)]
    return result


if __name__ == "__main__":
    with TestFramework(test_bootloadsflashintooverride) as frame:
        if frame != None:
            print(frame.test_run())
        else:
            print(TestFramework.failure())
