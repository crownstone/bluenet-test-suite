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
from BluenetTestSuite.firmwarecontrol.behaviourstore import *
from BluenetTestSuite.testframework.events import expect



def test_bootloadsflashintooverride_loopbody(FW, intensity):
    print("##### setup test_bootloadsflashintooverride_loopbody (intensity: {0}) #####".format(intensity))
    sendCommandToCrownstone(ControlType.RESET, [])
    time.sleep(60)  # wait for dimmer to power up...

    # override switch state
    print("sending switch command to crownstone {0}".format(intensity))
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    print("sending switch command to crownstone done")
    # need time for persistence of switch state to be pushed.
    time.sleep(15)

    # print("reset firmwarestate recorder")
    FW.clear()
    # print("restart test subject")
    sendCommandToCrownstone(ControlType.RESET, [])
    # print("allow device to reset and startup")
    time.sleep(3)

    # Test SwitchAggregator.overrideState
    expected_override_state = min(max(0, intensity), 100)

    response = expect(FW, "SwitchAggregator", 'overrideState', expected_override_state,
                      "overrideState should've been {0} after reset".format(
                          expected_override_state))

    if response is not None:
        return response

    # Test Relay.on. As dimming is turned on, this should only be true when the 8-th bit of the state is set explicitly.
    expected_relay_state = bool((intensity >> 7) & 1)

    response = expect(FW,"SafeSwitch", 'storedState.state.relay', expected_relay_state,
                      "relaystate should've been {0} after reset".format(
                            expected_relay_state))

    if response is not None:
        FW.print()
        return response

    return TestFramework.success()


def test_bootloadsflashintooverride(FW):
    setAllowDimming(True)
    sendClearBehaviourStoreEvent()

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
