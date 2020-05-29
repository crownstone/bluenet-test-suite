"""
Just a bunch of common methods
"""

import time

from BluenetLib.lib.packets.behaviour.SwitchBehaviour import SwitchBehaviour
from BluenetLib.lib.packets.behaviour.TwilightBehaviour import TwilightBehaviour
from BluenetLib.lib.protocol.BluenetTypes import ControlType, StateType

from BluenetTestSuite.firmwarecontrol.datatransport import *
from BluenetTestSuite.firmwarecontrol.InternalEventCodes import EventType


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


def sleepAfterUartCommand():
    time.sleep(0.5)

def sendBehaviour(index, behaviour):
    sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [index] + behaviour.getPacket())
    sleepAfterUartCommand()

def fullReset():
    print("Resetting crownstone and waiting for dimmer to have started for a cleaner test.")
    sendCommandToCrownstone(ControlType.RESET, [])
    for t in reversed(range(7)):
        print("sleeping for {0} more seconds".format((t + 1) * 10))
        time.sleep(10)

def getTime_uint32(hours, minutes, day=None):
    # day != 0  && (hours != 0 || minutes != 0): sunday
    # epoch is on a thursday, so we add 3*24*60*60 seconds
    dayoffset = 0
    if day is not None:
        dayoffset = (3 + day)
    return dayoffset * 24*60*60 + hours * 60*60 + minutes * 60

def setTime_uint32(time_as_uint32):
    sendCommandToCrownstone(ControlType.SET_TIME,
                            Conversion.uint32_to_uint8_array(time_as_uint32))
    sleepAfterUartCommand()

def setTime_hmd(hours, minutes, day=None):
    setTime_uint32(getTime_uint32(hours,
                           minutes,
                           day if day else 0))

def setAllowDimming(value):
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1 if value else 0])
    sleepAfterUartCommand()


def sendSwitchCommand(intensity):
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    sleepAfterUartCommand()


def sendClearSwitchAggregatorOverrideState():
    # this is getting fragile: if home is dumb it won't react.
    sendSwitchCommand(0xfe)
    sleepAfterUartCommand()

def sendClearSwitchAggregatorAggregatedState():
    # this is getting fragile: if home is dumb it won't react.
    sendSwitchCommand(0xfd)
    sleepAfterUartCommand()

def sendClearSwitchAggregatorOverrideAndAggregatedState():
        # this is getting fragile: if home is dumb it won't react.
        sendSwitchCommand(0xfc)
        sleepAfterUartCommand()

def sendSwitchAggregatorReset():
    sendEventToCrownstone(EventType.CMD_SWITCH_AGGREGATOR_RESET, [])

def sendSwitchCraftEvent():
    sendEventToCrownstone(EventType.CMD_SWITCH_TOGGLE, [])
    sleepAfterUartCommand()


def sendClearBehaviourStoreEvent():
    sendEventToCrownstone(0x100 + 170 + 6, [])

def sendCommandDumbMode(houseIsDumb):
    setstate_packet = []
    setstate_packet += Conversion.uint16_to_uint8_array(StateType.BEHAVIOUR_SETTINGS) # type id
    setstate_packet += [0x00, 0x00]     # state id 0
    setstate_packet += [0x00]           # persistence mode: store in ram
    setstate_packet += [0x00]           # reserved: must be 0
    # actual data: PROTOCOL.md#behaviour_settings_packet
    setstate_packet += Conversion.uint32_to_uint8_array(0x00 if houseIsDumb else 0x01)


    sendCommandToCrownstone(ControlType.SET_STATE, setstate_packet)
    # sendEventToCrownstone(EventType.BEHAVIOURHANDLER_SETTINGS, [0x00 if housIsDumb else 0x01])
    sleepAfterUartCommand()
