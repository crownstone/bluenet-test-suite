"""
Just a scratch that loads a cuckoo filter into the firmware in sevarl chunks.
"""
import time

from crownstone_core.packets.TrackableParser.TrackableParserPackets import *
from crownstone_core.packets.TrackableParser.TrackableParserCommands import *
from crownstone_core.protocol.BluenetTypes import ControlType

from crownstone_core.util.cuckoofilter import *
from crownstone_core.util.TrackableParser import MasterCrc, FilterCrc

from crownstone_uart import CrownstoneUart, UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics

from BluenetTestSuite.firmwarecontrol.datatransport import sendEventToCrownstone, sendCommandToCrownstone
from BluenetTestSuite.firmwarecontrol.InternalEventCodes import *

from bluenet_logs import BluenetLogs

# ------------------------------
# construct tracking filter data
# ------------------------------

#filterId 1
cuckoo = CuckooFilter(3, 2)
cuckoo.add([0xac, 0x23, 0x3f, 0x71, 0xca, 0x77][::-1])

trackingfilter = TrackingFilterData()
trackingfilter.filter = cuckoo.getData()

trackingfilter.metadata.protocol = 17
trackingfilter.metadata.version = 4567
trackingfilter.metadata.profileId = 0xae
trackingfilter.metadata.inputType = FilterInputType.MacAddress
trackingfilter.metadata.flags = 0b10101010

# ---------- another one for testing ----------
#filterId 0
cuckoo1 = CuckooFilter(4, 4)
cuckoo1.add([x for x in range (6)])

trackingfilter1 = TrackingFilterData()
trackingfilter1.filter = cuckoo.getData()

trackingfilter1.metadata.protocol = 17
trackingfilter1.metadata.version = 4567
trackingfilter1.metadata.profileId = 0x1
trackingfilter1.metadata.inputType = FilterInputType.MacAddress
trackingfilter1.metadata.flags = 0b10101010


# --------------------------
# MasterCrc
# --------------------------

masterCrc = MasterCrc([trackingfilter1, trackingfilter]) # be weary of filter id sorting...
print("filter crc:", FilterCrc(trackingfilter))
print("filter crc:", FilterCrc(trackingfilter1))
print("master crc:", masterCrc)

# --------------------------
# setup uart stuff
# --------------------------

bluenetLogs = BluenetLogs()
bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")

def successhandler(*args):
    print("success handler called", *args)

def failhandler(*args):
    print("fail handler called", *args)

def resulthandler(resultpacket):
    print("resulthandler called")
    if resultpacket.commandType == ControlType.TRACKABLE_PARSER_GET_SUMMARIES:
        try:
            print("deserialize trackable parser summary")
            summary = GetFilterSummariesReturnPacket()
            summary.setPacket(resultpacket.payload)
            print(summary)
        except ValueError as e:
            print("failed to deserialize result: ", resultpacket)
            print("error:",e)

uartfail = UartEventBus.subscribe(SystemTopics.uartWriteError,failhandler)
uartsucces = UartEventBus.subscribe(SystemTopics.uartWriteSuccess, successhandler)
uartresult = UartEventBus.subscribe(SystemTopics.resultPacket, resulthandler)

uart = CrownstoneUart()
uart.initialize_usb_sync(port='/dev/ttyACM0')
time.sleep(10)


# -------------------
# test infrastructure
# -------------------

def upload(trackingfilter, filterId, max_chunk_size):
    print(" ** starting upload **")
    filter_bytes = trackingfilter.getPacket()
    data_len = len(filter_bytes)
    for start_index in range(0, data_len, max_chunk_size):
        end_index = min(start_index + max_chunk_size, data_len)
        print(" -------- Send packet chunk (EVENT) -------- ", start_index,"-", end_index)

        upload_packet = UploadFilterCommandPacket()
        upload_packet.filterId = filterId
        upload_packet.totalSize = data_len
        upload_packet.chunkSize = end_index - start_index
        upload_packet.chunkStartIndex = start_index
        upload_packet.chunk = filter_bytes[start_index : end_index]

        wrapper = TrackableParserCommandWrapper(upload_packet)
        wrapper.commandProtocolVersion = 0

        sendCommandToCrownstone(ControlType.TRACKABLE_PARSER_UPLOAD_FILTER, wrapper.getPacket())
        time.sleep(0.5)


def remove(filterId):
    removePacket = RemoveFilterCommandPacket(filterId)
    wrapper = TrackableParserCommandWrapper(removePacket)
    wrapper.commandProtocolVersion = 0
    sendCommandToCrownstone(ControlType.TRACKABLE_PARSER_REMOVE_FILTER, wrapper.getPacket())

def commit(crc, version):
    commitCommand = CommitFilterChangesCommandPacket()
    commitCommand.masterCrc = crc
    commitCommand.masterVersion = version
    wrapper = TrackableParserCommandWrapper(commitCommand)
    wrapper.commandProtocolVersion = 0
    sendCommandToCrownstone(ControlType.TRACKABLE_PARSER_COMMIT_CHANGES, wrapper.getPacket())

def getStatus():
    statusCommand = GetFilterSummariesCommandPacket()
    wrapper = TrackableParserCommandWrapper(statusCommand)
    wrapper.commandProtocolVersion = 0
    sendCommandToCrownstone(ControlType.TRACKABLE_PARSER_GET_SUMMARIES, wrapper.getPacket())


# ----------------------------
# execute some commands
# ----------------------------

print("------------- upload filter ---------------");
upload(trackingfilter, filterId = 1,  max_chunk_size=10)
time.sleep(2)

print("------------- upload filter ---------------");
upload(trackingfilter1, filterId = 0,  max_chunk_size=10)
time.sleep(2)

print("------------- commit upload ---------------");
commit(crc = masterCrc, version = 1)
time.sleep(2)

getStatus()

time.sleep(60)
uart.stop()