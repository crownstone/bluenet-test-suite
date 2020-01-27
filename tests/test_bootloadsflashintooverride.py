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

# class MyTest(TestFramework):
#     def __init__(self):
        # super(MyTest,self).__init__(bootloadsflashintooverride_test)

def bootloadsflashintooverride_test(FW):
    print("setup device for this test")
    sendCommandToCrownstone(ControlType.SWITCH, [100])

    print("reset firmwarestate recorder")
    FW.clear()

    print("restart test subject")
    sendCommandToCrownstone(ControlType.RESET, [])

    print("allow device to reset and startup")
    time.sleep(0.5)

    print("check post conditions.")
    for obj in FW.statedict.values():
        if obj.get('typename') == 'SwSwitch':
            if obj.get('currentState.state.dimmer') == '0' and obj.get('currentState.state.relay') == '1':
                return "Result: success"

    return "Result: failure"

if __name__ == "__main__":
   with TestFramework(bootloadsflashintooverride_test) as frame:
       if frame != None:
           frame.testme()
       else:
           print("Result: failure")