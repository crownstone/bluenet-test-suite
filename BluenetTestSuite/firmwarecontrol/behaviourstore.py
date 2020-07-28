from crownstone_core.packets.behaviour.SwitchBehaviour import SwitchBehaviour
from crownstone_core.packets.behaviour.TwilightBehaviour import TwilightBehaviour

from BluenetTestSuite.firmwarecontrol.utils import *

def buildSwitchBehaviour(from_hours, to_hours, intensity):
    switchbehaviour = SwitchBehaviour()
    switchbehaviour.setTimeFrom(from_hours % 24, 0)
    switchbehaviour.setTimeTo(to_hours % 24, 0)
    switchbehaviour.setDimPercentage(intensity)
    switchbehaviour.setPresenceIgnore()
    return switchbehaviour


def buildTwilight(from_hours, to_hours, intensity):
    twilight = TwilightBehaviour()
    twilight.setTimeFrom(from_hours % 24, 0)
    twilight.setTimeTo(to_hours % 24, 0)
    twilight.setDimPercentage(intensity)
    return twilight


def sendBehaviour(index, behaviour):
    sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [index] + behaviour.getPacket())
    sleepAfterUartCommand()

def sendClearBehaviourStoreEvent():
    sendEventToCrownstone(0x100 + 170 + 6, [])
    sleepAfterUartCommand()
