import time
import uuid

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType

import datetime


def test_disabledimmingresolvestorelay_loopbody(FW, intensity):
    """

    """
    print("override switch state to be sure it is set to a dimmed value, and pause 15 sec to enforce persistence")
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])

    # need time for persistence of switch state to be pushed.
    time.sleep(15)

    print("##### test_disabledimmingresolvestorelay_loopbody setup #####")
    # print("reset firmwarestate recorder")
    FW.clear()

    # print("restart test subject")
    sendCommandToCrownstone(ControlType.RESET, [])

    # print("allow device to reset and startup")
    time.sleep(5)

    ### TODO check pre/post condition, add response

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
