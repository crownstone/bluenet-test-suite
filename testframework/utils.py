"""
Just a bunch of common methods
"""

import time

from BluenetLib.lib.packets.behaviour.Behaviour import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType
from firmwarecontrol.datatransport import *


def buildSwitchBehaviour(from_hours, to_hours, intensity):
    switchbehaviour = Behaviour()
    switchbehaviour.setTimeFrom(from_hours % 24, 0)
    switchbehaviour.setTimeTo(to_hours % 24, 0)
    switchbehaviour.setDimPercentage(intensity)
    return switchbehaviour


def buildTwilight(from_hours, to_hours, intensity):
    twilight = Twilight()
    twilight.setTimeFrom(from_hours % 24, 0)
    twilight.setTimeTo(to_hours % 24, 0)
    twilight.setDimPercentage(intensity)
    return twilight


def sleepAfterUartCommand():
    time.sleep(0.5)


def fullReset():
    print("Resetting crownstone and waiting for dimmer to have started for a cleaner test.")
    sendCommandToCrownstone(ControlType.RESET, [])
    for t in reversed(range(7)):
        print("sleeping for {0} more seconds".format((t + 1) * 10))
        time.sleep(10)

def getTime_uint32(hours, minutes, day=None):
    # day != 0  && (hours != 0 || minutes != 0): sunday
    # epoch is on a thursday, so we add 3*24*60*60 seconds
    return (3 + day if day else 0) * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60

def setTime_uint32(time_as_uint32):
    sendCommandToCrownstone(ControlType.SET_TIME,
                            Conversion.uint32_to_uint8_array(time_as_uint32))
    sleepAfterUartCommand()

def setTime_hmd(hours, minutes, day=None):
    setTime(getTime_uint32(hours,
                           minutes,
                           day if day else 0))


def sendBehaviour(index, behaviour):
    sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [index] + behaviour.getPacket())
    sleepAfterUartCommand()


def setAllowDimming(value):
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1])
    sleepAfterUartCommand()


def sendSwitchCommand(intensity):
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    sleepAfterUartCommand()


def sendClearSwitchAggregatorOverride():
    sendSwitchCommand(0xfe)
    sleepAfterUartCommand()


def sendSwitchCraftCommand():
    sendEventToCrownstone(0x100 + 20 + 2, [])
    sleepAfterUartCommand()


def sendClearBehaviourStoreEvent():
    sendEventToCrownstone(0x100 + 170 + 6, [])
    sleepAfterUartCommand()
