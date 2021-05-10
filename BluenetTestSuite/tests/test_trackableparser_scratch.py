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

def getMetaData():
    id = FilterInputDescription()
    id.format.type = AdvertisementSubdataType.MASKED_AD_DATA

    ffmad = FilterFormatMaskedAdData()
    ffmad.adType = 0xdd
    ffmad.mask = 0xabcdef12
    id.format.format.val = ffmad

    od = FilterOutputDescription()
    od.out_format.type = FilterOutputFormat.MAC_ADDRESS

    fmd = FilterMetaData()
    fmd.profileId = 0xAE
    fmd.inputDescription = id
    fmd.outputDescription = od

    return fmd

def cuckoo0():
    cuckoo = CuckooFilter(3, 2)
    cuckoo.add([0xac, 0x23, 0x3f, 0x71, 0xca, 0x77][::-1])
    return cuckoo


def cuckoo1():
    cuckoo = CuckooFilter(4, 4)
    for i in range(5):
        cuckoo.add([(i*6+x) % 0x100 for x in range(6)][::-1])

    return cuckoo


def filter0():
    af = AssetFilter()
    af.metadata = getMetaData()
    af.filterdata.val = cuckoo0().getData()
    return af


def filter1():
    af = AssetFilter()
    af.metadata = getMetaData()
    af.filterdata.val = cuckoo1().getData()
    return af


# -------------------------
# uart message bus handlers
# -------------------------

def successhandler(*args):
    print("success handler called", *args)

def failhandler(*args):
    print("fail handler called", *args)


def resulthandler(resultpacket):
    print("resulthandler called")
    if resultpacket.commandType == ControlType.ASSET_FILTER_GET_SUMMARIES:
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
    print("total filter bytes:", data_len, " filter crc: ", hex(crc16ccitt(filter_bytes)), " fitlerid: " , filterId)
    for start_index in range(0, data_len, max_chunk_size):
        end_index = min(start_index + max_chunk_size, data_len)
        print(" -------- Send packet chunk (EVENT) -------- ", start_index,"-", end_index)

        upload_packet = UploadFilterCommandPacket()
        upload_packet.filterId = filterId
        upload_packet.totalSize = data_len
        upload_packet.chunkSize = end_index - start_index
        upload_packet.chunkStartIndex = start_index
        upload_packet.chunk = filter_bytes[start_index : end_index]

        sendCommandToCrownstone(ControlType.ASSET_FILTER_UPLOAD, upload_packet.getPacket())
        time.sleep(0.5)


def remove(filterId):
    removePacket = RemoveFilterCommandPacket(filterId)
    sendCommandToCrownstone(ControlType.ASSET_FILTER_REMOVE, removePacket.getPacket())

def commit(crc, version):
    commitCommand = CommitFilterChangesCommandPacket()
    commitCommand.masterCrc = crc
    commitCommand.masterVersion = version
    sendCommandToCrownstone(ControlType.ASSET_FILTER_COMMIT_CHANGES, commitCommand.getPacket())

def getStatus():
    sendCommandToCrownstone(ControlType.ASSET_FILTER_GET_SUMMARIES, [])


if __name__ == "__main__":
    # build a few filters
    trackingfilters = [filter0(), filter1()]

    masterCrc = MasterCrc(trackingfilters)  # be weary of filter id sorting...
    for f in trackingfilters:
        print("filter crc:", hex(FilterCrc(f)))
    print("master crc:", hex(masterCrc))

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