from crownstone_core.util.Conversion import Conversion
from crownstone_core.protocol.BlePackets import ControlPacket

from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.uartPackets.UartWrapperPacket import UartWrapperPacket
from crownstone_uart.core.uart.UartTypes import UartTxType, UartMessageType
from crownstone_uart.topics.SystemTopics import SystemTopics

import time

def sleepAfterUartCommand():
    time.sleep(1)

def sendEventToCrownstone(cs_event_type, cs_event_data):
    """
    To send events over the firmware internal event bus use this method.
    eventtype: CS_TYPE
    eventdata: corresponds to eventtype.
    """
    uart_message = []
    uart_message += Conversion.uint16_to_uint8_array(UartTxType.MOCK_INTERNAL_EVT)
    uart_message += Conversion.uint16_to_uint8_array(cs_event_type)
    uart_message += cs_event_data
    uart_warpper_packet = UartWrapperPacket(UartMessageType.UART_MESSAGE,uart_message).getPacket()
    UartEventBus.emit(SystemTopics.uartWriteData, uart_warpper_packet)
    sleepAfterUartCommand()

def sendCommandToCrownstone(commandtype, packetcontent):
    """
    Send a control command to the crownstone with the given commandtype.
    commandtype: as documented in PROTOCOL.md#command-types
    packetcontent: as documented in PROTOCOL.md
    """
    controlPacket = ControlPacket(commandtype)
    controlPacket.appendByteArray(packetcontent)
    uartPacket = UartWrapperPacket(UartTxType.CONTROL, controlPacket.getPacket()).getPacket()
    UartEventBus.emit(SystemTopics.uartWriteData, uartPacket)
    sleepAfterUartCommand()
