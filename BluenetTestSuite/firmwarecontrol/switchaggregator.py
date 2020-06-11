from enum import IntEnum

from BluenetTestSuite.firmwarecontrol.utils import *
from BluenetTestSuite.firmwarecontrol.InternalEventCodes import EventType

class SwitchCommandValue(IntEnum):
    CS_SWITCH_CMD_VAL_OFF = 0
    # Dimmed from 1 - 99
    CS_SWITCH_CMD_VAL_FULLY_ON = 100
    CS_SWITCH_CMD_VAL_NONE = 128      # For printing: the value is set to nothing.
    CS_SWITCH_CMD_VAL_DEBUG_RESET_ALL = 129
    CS_SWITCH_CMD_VAL_DEBUG_RESET_AGG = 130
    CS_SWITCH_CMD_VAL_DEBUG_RESET_OVERRIDE = 131
    CS_SWITCH_CMD_VAL_DEBUG_RESET_AGG_OVERRIDE = 132

    CS_SWITCH_CMD_VAL_TOGGLE = 253    # Switch OFF when currently on, switch to SMART_ON when currently off.
    CS_SWITCH_CMD_VAL_BEHAVIOUR = 254 # Switch to the value according to behaviour rules.
    CS_SWITCH_CMD_VAL_SMART_ON = 255   # Switch on, the value will be determined by behaviour rules.


def sendSwitchCommand(intensity):
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    sleepAfterUartCommand()


def sendSwitchCraftEvent():
    sendEventToCrownstone(EventType.CMD_SWITCH_TOGGLE, [])
    sleepAfterUartCommand()

def sendClearSwitchAggregatorOverrideState():
    # this is getting fragile: if home is dumb it won't react.
    sendSwitchCommand(SwitchCommandValue.CS_SWITCH_CMD_VAL_DEBUG_RESET_OVERRIDE)
    sleepAfterUartCommand()

def sendClearSwitchAggregatorAggregatedState():
    # this is getting fragile: if home is dumb it won't react.
    sendSwitchCommand(SwitchCommandValue.CS_SWITCH_CMD_VAL_DEBUG_RESET_AGG)
    sleepAfterUartCommand()

def sendClearSwitchAggregatorOverrideAndAggregatedState():
    # this is getting fragile: if home is dumb it won't react.
    sendSwitchCommand(SwitchCommandValue.CS_SWITCH_CMD_VAL_DEBUG_RESET_AGG_OVERRIDE)
    sleepAfterUartCommand()

def sendSwitchAggregatorReset():
    sendSwitchCommand(SwitchCommandValue.CS_SWITCH_CMD_VAL_DEBUG_RESET_ALL)
    sleepAfterUartCommand()

