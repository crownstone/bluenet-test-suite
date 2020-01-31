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
    print("##### test_disabledimmingresolvestorelay_loopbody #####")

    # print("reset firmwarestate recorder")
    FW.clear()

    # print("restart test subject and wait for dimmer to have started")
    sendCommandToCrownstone(ControlType.RESET, [])
    for t in reversed(range(7)):
        time.sleep(10)
        # print("sleeping for {0} more seconds".format(t*10))

    # print("set dimming allowed true and put a value in there.")
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1])
    time.sleep(0.5)
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    time.sleep(0.5)

    FW.print()
    FW.printhistory()

    # print("check override state")
    failures = FW.assertFindFailures("SwitchAggregator", 'overrideState', intensity)
    if failures:
        return TestFramework.failure("Override not set after switch command")

    # print("check dimmer value intensity")
    failures = FW.assertFindFailures("HwSwitch", 'dimmer', intensity)
    if failures:
        return TestFramework.failure("Dimmer not set to correct intensity")

    # print("check relay value 0")
    failures = FW.assertFindFailures("HwSwitch", 'relay', False)
    if failures:
        return TestFramework.failure("Relay should be off when dimming is allowed")

    # print("set dimming allowed false")
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [0])
    time.sleep(0.5)

    # print("check override hasn't changed")
    failures = FW.assertFindFailures("SwitchAggregator", 'overrideState', intensity)
    if failures:
        return TestFramework.failure("Override changed after dimming disallowed")

    # print("check dimmer is deactivated")
    failures = FW.assertFindFailures("HwSwitch", 'dimmer', 0)
    if failures:
        return TestFramework.failure("Dimmer wasn't disabled after dimming disallowed")

    # print("check relay value is activated")
    failures = FW.assertFindFailures("HwSwitch", 'relay', intensity > 0)
    if failures:
        return TestFramework.failure("Relay did not pick up correct value after dimming disallowed")

    return TestFramework.success()


def test_disabledimmingresolvestorelay(FW):
    """
    When dimming changes to the value 'disallowed' the crownstone must change from
    IGBT mode to relay.
    """
    print("##### test_disabledimmingresolvestorelay #####")

    result = []
    for intensity in [0]:#[0,50,100]:
        result += [test_disabledimmingresolvestorelay_loopbody(FW, intensity)]
    return result


if __name__ == "__main__":
    with TestFramework(test_disabledimmingresolvestorelay) as frame:
        if frame != None:
            print(frame.test_run())
        else:
            print(TestFramework.failure())
