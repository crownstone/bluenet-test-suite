from crownstone_core.util.Conversion import Conversion
from crownstone_core.protocol.BlePackets import ControlPacket

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartWrapper import UartWrapper
from crownstone_uart.core.uart.UartTypes import UartTxType
from crownstone_uart.topics.SystemTopics import SystemTopics

import time

def sleepAfterUartCommand():
    time.sleep(1)

def sendEventToCrownstone(eventtype, eventdata):
    """
    To send events over the firmware internal event bus use this method.
    eventtype: CS_TYPE
    eventdata: corresponds to eventtype.
    """
    payload = []
    payload += Conversion.uint16_to_uint8_array(eventtype)
    payload += eventdata
    uartPacket = UartWrapper(UartTxType.MOCK_INTERNAL_EVT,payload).getPacket()
    UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)
    sleepAfterUartCommand()

def sendCommandToCrownstone(commandtype, packetcontent):
    """
    Send a control command to the crownstone with the given commandtype.
    commandtype: as documented in PROTOCOL.md#command-types
    packetcontent: as documented in PROTOCOL.md
    """
    controlPacket = ControlPacket(commandtype)
    controlPacket.appendByteArray(packetcontent)
    uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket.getPacket()).getPacket()
    UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)
    sleepAfterUartCommand()
