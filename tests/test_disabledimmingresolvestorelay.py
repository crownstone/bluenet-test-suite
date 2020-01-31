import time
import uuid

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType

import datetime


def test_disabledimmingresolvestorelay_loopbody(FW, intensity):
    """
    Clear firmware state tracker.
    Resets firmware and wait for reboot.
    Sets allow dimming to true.
    Sets switch to override state [intensity]. (does not wait for persistence)
    Sets allow dimming to false.

    Assumes:
    No behaviours persisted.

    Expect:
    after setting intensity, relay should be off and dimmer value should be equal to [intensity].
    after disallowing dimming, dimmer value should be equal to 0.
    after disallowing dimming, if intensity > 0: the relay should be on; else off.

    """
    # print("reset firmwarestate recorder")
    FW.clear()

    # print("restart test subject")
    sendCommandToCrownstone(ControlType.RESET, [])
    time.sleep(5)

    # set dimming allowed true and put a value in there.
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1])
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    time.sleep(0.5)

    print("##### test_disabledimmingresolvestorelay_loopbody setup #####")

    # check override state
    if FW.assertFindFailures("SwitchAggregator", 'overrideState', intensity):
        return TestFramework.failure("Override not set after switch command")

    # check dimmer value intensity
    if FW.assertFindFailures("HwSwitch", 'dimmer', intensity):
        return TestFramework.failure("Dimmer not set to correct intensity")

    # check relay value 0
    if FW.assertFindFailures("HwSwitch", 'relay', 0):
        return TestFramework.failure("Relay should be off when dimming is allowed")

    # set dimming allowed false
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [0])

    # check override hasn't changed
    if FW.assertFindFailures("SwitchAggregator", 'overrideState', intensity):
        return TestFramework.failure("Override changed after dimming disallowed")

    # check dimmer is deactivated
    if FW.assertFindFailures("HwSwitch", 'dimmer', 0):
        return TestFramework.failure("Dimmer wasn't disabled after dimming disallowed")

    # check relay value is activated
    if FW.assertFindFailures("HwSwitch", 'relay', 1 if intensity > 0 else 0):
        return TestFramework.failure("Relay did not pick up correct value after dimming disallowed")

    return TestFramework.failure()


def test_disabledimmingresolvestorelay(FW):
    """
    When dimming changes to the value 'disallowed' the crownstone must change from
    IGBT mode to relay.
    """
    print("##### test_disabledimmingresolvestorelay #####")

    result = []
    for intensity in [0,50,100]:
        result += [test_disabledimmingresolvestorelay_loopbody(FW, intensity)]
    return result


if __name__ == "__main__":
    with TestFramework(test_disabledimmingresolvestorelay) as frame:
        if frame != None:
            print(frame.test_run())
        else:
            print(TestFramework.failure())
