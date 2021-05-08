"""
Just a scratch that loads a few cuckoo filters into the firmware in chunks,
then commits them and requests their status.
"""
import time

from crownstone_core.packets.assetFilterStore.FilterIOPackets import *
from crownstone_core.packets.assetFilterStore.FilterDescriptionPackets import *

from crownstone_core.packets.assetFilterStore.FilterMetaDataPackets import *
from crownstone_core.packets.assetFilterStore.AssetFilterStoreCommands import *

from crownstone_core.protocol.BluenetTypes import ControlType

from crownstone_core.util.Cuckoofilter import *
from crownstone_core.util.AssetFilterStore import MasterCrc, FilterCrc

from crownstone_uart import CrownstoneUart, UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics

from BluenetTestSuite.firmwarecontrol.datatransport import sendCommandToCrownstone

from bluenet_logs import BluenetLogs

# ------------------------------
# construct tracking filter data
# ------------------------------

class myEnum(IntEnum):
    V= 0
    W=1
    def get(self):
        return int(self)
    def set(self, v):
        self._value_ = v

a0 = AdvertisementSubdata()
a0.type = AdvertisementSubdataType()
print(a0.getPacket())

a1 = AdvertisementSubdata()
a1.type = AdvertisementSubdataType.AD_DATA
print(a1.getPacket())

a2 = AdvertisementSubdata()
a2.type = AdvertisementSubdataType.MASKED_AD_DATA
a2.format.loadType()
a2.format.mask = 0x12345678
a2_packet = a2.getPacket()
print(a2_packet)

a3 = AdvertisementSubdata()
a3.setPacket(a2_packet)
print(a3)


# DEBUG
quit()


def filter0():
    cuckoo = CuckooFilter(3, 2)
    cuckoo.add([0xac, 0x23, 0x3f, 0x71, 0xca, 0x77][::-1])

    trackingfilter = TrackingFilterData()
    trackingfilter.filter = cuckoo.getData()

    trackingfilter.metadata.protocol = 17
    trackingfilter.metadata.version = 4567
    trackingfilter.metadata.profileId = 0xae
    trackingfilter.metadata.inputType = FilterInputType.MacAddress
    trackingfilter.metadata.flags = 0b10101010
    return  trackingfilter

def filter1():
    cuckoo = CuckooFilter(4, 4)
    cuckoo.add([x for x in range (6)])

    trackingfilter = TrackingFilterData()
    trackingfilter.filter = cuckoo.getData()

    trackingfilter.metadata.protocol = 17
    trackingfilter.metadata.version = 4567
    trackingfilter.metadata.profileId = 0x1
    trackingfilter.metadata.inputType = FilterInputType.MacAddress
    trackingfilter.metadata.flags = 0b10101010
    return trackingfilter


# -------------------------
# uart message bus handlers
# -------------------------

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


if __name__ == "__main__":
    # build a few filters
    trackingfilters = [filter0(), filter1()]

    masterCrc = MasterCrc(trackingfilters)  # be weary of filter id sorting...
    for f in trackingfilters:
        print("filter crc:", FilterCrc(f))
    print("master crc:", masterCrc)

    # setup uart stuff
    bluenetLogs = BluenetLogs()
    bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")

    uartfail = UartEventBus.subscribe(SystemTopics.uartWriteError, failhandler)
    uartsucces = UartEventBus.subscribe(SystemTopics.uartWriteSuccess, successhandler)
    uartresult = UartEventBus.subscribe(SystemTopics.resultPacket, resulthandler)

    uart = CrownstoneUart()
    uart.initialize_usb_sync(port='/dev/ttyACM0')
    time.sleep(10)

    # execute some commands
    for i, f in enumerate(trackingfilters):
        print("------------- upload filter ---------------");
        upload(f, filterId = i,  max_chunk_size=10)
        time.sleep(2)

    print("------------- commit upload ---------------");
    commit(crc = masterCrc, version = 1)
    time.sleep(2)

    getStatus()

    # let it run for a bit
    time.sleep(60)
    uart.stop()