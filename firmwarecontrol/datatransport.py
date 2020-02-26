# from BluenetLib import Bluenet
# from BluenetLib import UsbTopics
from BluenetLib import BluenetEventBus

from BluenetLib.lib.core.uart.UartTypes import UartTxType
from BluenetLib.lib.util.Conversion import Conversion
from BluenetLib.lib.core.uart.UartWrapper import UartWrapper
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.protocol.BlePackets import ControlPacket

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
    BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)

def sendCommandToCrownstone(commandtype, packetcontent):
    """
    Send a control command to the crownstone with the given commandtype.
    commandtype: as documented in PROTOCOL.md
    packetcontent: as documented in PROTOCOL.md
    """
    controlPacket = ControlPacket(commandtype)
    controlPacket.appendByteArray(packetcontent)
    uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket.getPacket()).getPacket()
    print("sendCommandToCrownstone( type:{0} )".format(commandtype)); print(uartPacket)
    BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)
