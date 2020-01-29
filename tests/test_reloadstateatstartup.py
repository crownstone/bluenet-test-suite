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
import time, sys

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType


def test_bootloadsflashintooverride_loopbody(FW, intensity):
    print("#####")
    print("setup test_bootloadsflashintooverride_loopbody (intensity: {0})".format(intensity))
    print("-----")
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])

    time.sleep(15)

    print("reset firmwarestate recorder")
    FW.clear()

    print("restart test subject")
    sendCommandToCrownstone(ControlType.RESET, [])

    print("allow device to reset and startup")
    time.sleep(10)

    print("-----")
    print("check post conditions.")
    FW.print()
    print("-----")

    expected_override_state = min(max(0, intensity), 100)
    expected_relay_state = bool( (intensity >> 7) & 1 )

    if FW.assertFindFailures("SwitchAggregator", 'overrideState', expected_override_state):
        return TestFramework.failure("overrideState should've been {0} after reset".format(expected_override_state))
    elif FW.assertFindFailures("HwSwitch", 'relay', expected_relay_state):
        return TestFramework.failure("relaystate should've been {0} after reset".format(expected_relay_state))
    else:
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
