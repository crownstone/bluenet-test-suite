"""
Just a scratch that loads a cuckoo filter into the firmware in sevarl chunks.
"""
import time

from BluenetTestSuite.firmwarecontrol.behaviourstore import sendBehaviour, buildTwilight, sendClearBehaviourStoreEvent
from crownstone_core.protocol.BluenetTypes import ControlType
from crownstone_core.packets.TrackableParser.TrackableParserPackets import *
from crownstone_core.packets.TrackableParser.TrackableParserCommands import *


from crownstone_core.util.cuckoofilter import *

from crownstone_uart import CrownstoneUart, UartEventBus
from BluenetTestSuite.firmwarecontrol.datatransport import sendCommandToCrownstone, sendEventToCrownstone

from bluenet_logs import BluenetLogs
from crownstone_uart.topics.SystemTopics import SystemTopics

bluenetLogs = BluenetLogs()
bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")

# construct cuckoo filter
cuckoo = CuckooFilter(8, 2)
some_element = [i % 0x100 for i in range(10)]
cuckoo.add(some_element)

print("filter size: ", cuckoo.size())
print(cuckoo.contains(some_element))

# construct tracking filter
trackingfilter = TrackingFilterData()
trackingfilter.metadata.protocol = 1
trackingfilter.metadata.version = 45
trackingfilter.metadata.profileId = 0
trackingfilter.metadata.inputType = FilterInputType.MacAddress
trackingfilter.metadata.flags = 0x00
trackingfilter.filter = cuckoo.getData()

print("metadata", len(trackingfilter.metadata.getPacket()), trackingfilter.metadata.getPacket())
print("filter  ", len(trackingfilter.filter.getPacket()), trackingfilter.filter.getPacket())
print("combined", len(trackingfilter.getPacket()), trackingfilter.getPacket())

def upload(cuckoofilter, max_chunk_size):
    filter_bytes = cuckoofilter.getPacket()
    data_len = len(filter_bytes)
    for start_index in range(0, data_len, max_chunk_size):
        end_index = min(start_index + max_chunk_size, data_len)
        print(" -------- Send packet chunk (EVENT) -------- ", start_index,"-", end_index)

        upload_packet = UploadFilterCommandPacket()
        upload_packet.filterId = 1
        upload_packet.totalSize = data_len
        upload_packet.chunkSize = end_index - start_index
        upload_packet.chunkStartIndex = start_index
        upload_packet.chunk = filter_bytes[start_index : end_index]
        print([hex(x) for x in upload_packet.getPacket()])

        sendEventToCrownstone(455, upload_packet.getPacket())
        time.sleep(1)
        # sendCommandToCrownstone(ControlType.TRACKABLE_PARSER_UPLOAD_FILTER, upload_packet.getPacket())

def loopbacktest(*args):
    print("loopback", *args)

def successhandler(*args):
    print("success handler called", *args)

def failhandler(*args):
    print("fail handler called", *args)

uartfail = UartEventBus.subscribe(SystemTopics.uartWriteError,failhandler)
uartsucces = UartEventBus.subscribe(SystemTopics.uartWriteSuccess, successhandler)
loopback = UartEventBus.subscribe(SystemTopics.uartWriteData, loopbacktest)

uart = CrownstoneUart()

uart.initialize_usb_sync(port='/dev/ttyACM0')
print(" ** starting upload **")
print("---------------------------------")
time.sleep(10)
upload(cuckoo, max_chunk_size=10)

time.sleep(30)
uart.stop()