# from BluenetLib import Bluenet
# from BluenetLib import UsbTopics
from BluenetLib import BluenetEventBus

from BluenetLib.lib.core.uart.UartTypes import UartTxType
from BluenetLib.lib.util.Conversion import Conversion
from BluenetLib.lib.core.uart.UartWrapper import UartWrapper
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.protocol.BlePackets import ControlPacket


def initializeUSB(bluenet_instance, portname, a_range):
    """
    Tries to connect to the given busname with the given index. If it finds one it will break,
    logs where there is none. And returns full connected port name as string on success/None object on failure.
    """
    for i in a_range:
        try:
            port = "/dev/{0}{1}".format(portname, i)
            bluenet_instance.initializeUSB(port)
            return port
        except Exception as err:
            print("coudn't find '/dev/ttyACM{0}', trying next port".format(i))
            print(err)
    return None


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
    # print("sendCommandToCrownstone( type:{0} )".format(commandtype)); print(uartPacket)
    BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)
