"""
Just a scratch that loads a few cuckoo filters into the firmware in chunks,
then commits them and requests their status.
"""
import time
# import logging
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from crownstone_core.packets.assetFilter.AssetFilterCommands import *

from crownstone_core.util import AssetFilterUtil
from crownstone_core.util.CRC import crc32

from crownstone_core.protocol.BluenetTypes import ControlType

from crownstone_uart import CrownstoneUart, UartEventBus
from crownstone_uart.core.uart.uartPackets.AssetMacReport import *
from crownstone_uart.core.uart.uartPackets.AssetSidReport import *
from crownstone_uart.topics.SystemTopics import SystemTopics
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket
from crownstone_uart.core.uart.UartTypes import UartRxType
from crownstone_uart.core.uart.uartPackets.NearestCrownstones import NearestCrownstoneTrackingUpdate

from BluenetTestSuite.firmwarecontrol.datatransport import sendCommandToCrownstone
from BluenetTestSuite.utils.exactmacfilter import *
from BluenetTestSuite.utils.cuckoofilter import *
from BluenetTestSuite.utils.filtercommands import *

from bluenet_logs import BluenetLogs

# -------------------------
# uart message bus handlers
# -------------------------



def successhandler(*args):
    #print("success handler called", *args)
    pass

def failhandler(*args):
    # print("fail handler called", *args)
    pass

def uartmsghandler(msg: UartMessagePacket):
    if msg.opCode == UartRxType.NEAREST_CROWNSTONE_TRACKING_UPDATE:
        print(f"Received NEAREST_CROWNSTONE_TRACKING_UPDATE: {msg.payload}")
        packet = NearestCrownstoneTrackingUpdate()
        packet.setPacket(msg.payload)
        print(packet)

    if msg.opCode == UartRxType.UART_OPCODE_TX_ASSET_RSSI_MAC_DATA:
        print(f"Received UART_OPCODE_TX_ASSET_RSSI_MAC_DATA: {msg.payload}")
        report : AssetMacReport = msg.payload
        print(report)

    if msg.opCode == UartRxType.UART_OPCODE_TX_ASSET_RSSI_SID_DATA:
        print(f"Received UART_OPCODE_TX_ASSET_RSSI_SID_DATA: {msg.payload}")
        report : AssetSidReport = msg.payload
        print(report)

def resulthandler(resultpacket):
    print("resulthandler called")
    print(resultpacket)
    if resultpacket.commandType == ControlType.ASSET_FILTER_GET_SUMMARIES:
        try:
            print("deserialize trackable parser summary")
            print(resultpacket.payload)
            summary = GetFilterSummariesReturnPacket()
            print(summary)
            summary.setPacket(resultpacket.payload)
            print(summary)
        except ValueError as e:
            print("failed to deserialize result: ", resultpacket)
            print("error:",e)

# -------------------
# test infrastructure
# -------------------


if __name__ == "__main__":
    # setup uart stuff
    bluenetLogs = BluenetLogs()
    bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")

    uartfail = UartEventBus.subscribe(SystemTopics.uartWriteError, failhandler)
    uartsucces = UartEventBus.subscribe(SystemTopics.uartWriteSuccess, successhandler)
    uartresult = UartEventBus.subscribe(SystemTopics.resultPacket, resulthandler)
    uartmsg = UartEventBus.subscribe(SystemTopics.uartNewMessage, uartmsghandler)


    uart = CrownstoneUart()
    uart.initialize_usb_sync(port='/dev/ttyACM0')
    time.sleep(5)

    trackingfilters = []
    # trackingfilters.append(filter0())
    # trackingfilters.append(filter1())
    # trackingfilters.append(filterAlex())
    # trackingfilters.append(filterBlyott())
    trackingfilters.append(filterExactMacInMacOut())
    # trackingfilters.append(filterExactMacInShortIdOut())
    # trackingfilters.append(filterExactExclude())

    # TODO: build filter with new sid+rssi output

    masterCrc = removeAllFilters()
    masterCrc = uploadFilters()
    finalizeFilterUpload(masterCrc)
    getStatus()

    # let it run for a bit
    try:
        while True:
            time.sleep(1)
            print(" * script still running * ")
    except:
        print("escaped while loop")

    uart.stop()