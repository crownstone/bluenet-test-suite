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

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.firmwarecontrol.datatransport import *
from BluenetTestSuite.testframework.events import expect
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

    # Test SwitchAggregator.overrideState
    expected_override_state = min(max(0, intensity), 100)
    # if FW.assertFindFailures("SwitchAggregator", 'overrideState', expected_override_state):
    #     FW.print()
    #     return TestFramework.failure("overrideState should've been {0} after reset".format(
    #             expected_override_state))

    response = expect(FW, "SwitchAggregator", 'overrideState', expected_override_state,
                      "overrideState should've been {0} after reset".format(
                          expected_override_state))

    if response is not None:
        return response

    # Test Relay.on
    expected_relay_state = bool((intensity >> 7) & 1)
    response = expect(FW,"Relay", 'on', expected_relay_state,
                      "relaystate should've been {0} after reset".format(
                            expected_relay_state))

    if response is not None:
        return response
    # if FW.assertFindFailures("Relay", 'on', expected_relay_state):
    #     FW.print()
    #     return TestFramework.failure("relaystate should've been {0} after reset".format(
    #             expected_relay_state))

    return TestFramework.success()


def test_bootloadsflashintooverride(FW):
    result = []
    for intensity in [0, 100,128]:
        result += [test_bootloadsflashintooverride_loopbody(FW, intensity)]
    return result


if __name__ == "__main__":
    with TestFramework(test_bootloadsflashintooverride) as frame:
        if frame != None:
            for result in frame.test_run():
                print(result)
        else:
            print(TestFramework.failure())
