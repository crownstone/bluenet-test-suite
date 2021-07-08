"""
Just a scratch that loads a few cuckoo filters into the firmware in chunks,
then commits them and requests their status.
"""
import time


from crownstone_core.packets.assetFilter.FilterDescriptionPackets import *
from crownstone_core.packets.assetFilter.FilterIOPackets import *
from crownstone_core.packets.assetFilter.FilterMetaDataPackets import *
from crownstone_core.packets.assetFilter.AssetFilterCommands import *

from crownstone_core.util import AssetFilterUtil
from crownstone_core.util.CRC import crc32
from crownstone_core.util.Cuckoofilter import CuckooFilter

from crownstone_core.protocol.BluenetTypes import ControlType

from crownstone_uart import CrownstoneUart, UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics

from BluenetTestSuite.firmwarecontrol.datatransport import sendCommandToCrownstone

from bluenet_logs import BluenetLogs

# ------------------------------
# construct tracking filter data
# ------------------------------


# --------- filter 0 --------
def getMetaData0():
    id = FilterInputDescription()
    id.format.type = AdvertisementSubdataType.MAC_ADDRESS

    # id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
    # ffmad = FilterFormatMaskedAdData()
    # ffmad.adType = 0xdd
    # ffmad.mask = 0xabcdef12
    # id.format.format.val = ffmad

    od = FilterOutputDescription()
    od.out_format.type = FilterOutputFormat.MAC_ADDRESS

    fmd = FilterMetaData()
    fmd.profileId = 0xAE
    fmd.inputDescription = id
    fmd.outputDescription = od

    return fmd

def cuckoo0():
    cuckoo = CuckooFilter(3, 2)
    cuckoo.add([0xac, 0x23, 0x3f, 0x71, 0xca, 0x77][::-1]) # D15N minew beacon on my desk
    return cuckoo

def filter0():
    af = AssetFilter()
    af.metadata = getMetaData0()
    af.filterdata.val = cuckoo0().getData()
    return af

# --------- filter 1 ------------


def getMetaData1():
    id = FilterInputDescription()
    id.format.type = AdvertisementSubdataType.MAC_ADDRESS

    # id.format.type = AdvertisementSubdataType.AD_DATA
    # ffad = FilterFormatAdData()
    # ffad.adType = 0x16 # servicedata
    # id.format.format.val = ffad

    id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
    ffmad = FilterFormatMaskedAdData()
    ffmad.adType = 0x16  # type == servicedata
    # ffmad.mask = 0xffffffff # mask out 'nothing'
    ffmad.mask = 0b1111  # mask out only last few bytes
    id.format.format.val = ffmad

    od = FilterOutputDescription()
    od.out_format.type = FilterOutputFormat.MAC_ADDRESS

    fmd = FilterMetaData()
    fmd.profileId = 0xAE
    fmd.inputDescription = id
    fmd.outputDescription = od

    return fmd

def cuckoo1():
    cuckoo = CuckooFilter(4, 4)
    # service data (type 0x16) content of one of the advertisements that
    # the D15N minew beacon broadcasts.
    # cuckoo.add([0xaa,0xfe,0x10,0xe8,0x01,0x6d,0x69,0x6e,0x65,0x77,0x00])

    # cuckoo.add([0xaa, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # cuckoo.add([0xaa, 0xfe, 0x10,0xe8])
    cuckoo.add([0xaa,0xfe,0x10,0xe8])

    return cuckoo

def filter1():
    af = AssetFilter()
    af.metadata = getMetaData1()
    af.filterdata.val = cuckoo1().getData()
    return af



# ------------ Alex' filter -----------


def getMetaDataAlex():
    id = FilterInputDescription()
    id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
    ffmad = FilterFormatMaskedAdData()
    ffmad.adType = 0xFF
    ffmad.mask = 0b11
    id.format.format.val = ffmad

    od = FilterOutputDescription()
    od.out_format.type = FilterOutputFormat.MAC_ADDRESS

    fmd = FilterMetaData()
    fmd.profileId = 0xFF
    fmd.type = FilterType.EXACT_MATCH
    fmd.inputDescription = id
    fmd.outputDescription = od

    return fmd

def cuckooAlex():
    cuckoo = CuckooFilter(0, 2)
    cuckoo.add([0xcd, 0x09])
    # cuckoo.add([0xcd, 0x09][::-1])
    return cuckoo

def filterAlex():
    af = AssetFilter()
    af.metadata = getMetaDataAlex()
    af.filterdata.val = cuckooAlex().getData()
    return af


# ----------------- exact match filter ----------------------


def exactFilter():
    filly = ExactMatchFilterData(itemCount=2,itemSize=6)
    filly.itemArray.val = []
    filly.itemArray.val += [int(x, 16) for x in "60:c0:bf:28:0d:ae".split(":")]
    filly.itemArray.val += [int(x, 16) for x in "60:c0:bf:28:0d:ae".split(":")][::-1]
    return filly


def getMetaDataExactMacOut():
    id = FilterInputDescription()
    id.format.type = AdvertisementSubdataType.MAC_ADDRESS

    od = FilterOutputDescription()
    od.out_format.type = FilterOutputFormat.MAC_ADDRESS

    fmd = FilterMetaData()
    fmd.profileId = 0x05
    fmd.type = FilterType.EXACT_MATCH
    fmd.inputDescription = id
    fmd.outputDescription = od

    return fmd


def getMetaDataExactShortIdOut():
    id = FilterInputDescription()
    id.format.type = AdvertisementSubdataType.MAC_ADDRESS

    od = FilterOutputDescription()
    od.out_format = FilterOutputFormat.SHORT_ASSET_ID
    od.in_format.loadType()
    od.in_format.val.type = AdvertisementSubdataType.MAC_ADDRESS

    fmd = FilterMetaData()
    fmd.profileId = 0x05
    fmd.type = FilterType.EXACT_MATCH
    fmd.inputDescription = id
    fmd.outputDescription = od

    print("fmd: ", fmd.getPacket())
    return fmd

def filterExactMacOut():
    af = AssetFilter()
    af.metadata = getMetaDataExactMacOut()
    af.filterdata.val = exactFilter()
    return af

def filterExactShortIdOut():
    af = AssetFilter()
    af.metadata = getMetaDataExactShortIdOut()
    af.filterdata.val = exactFilter()
    return af

# ------------ Blyott filter -----------


def getMetaDataBlyott():
    id = FilterInputDescription()
    id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
    ffmad = FilterFormatMaskedAdData()
    ffmad.adType = 0xFF
    ffmad.mask = 0b11
    id.format.format.val = ffmad

    od = FilterOutputDescription()
    od.out_format.type = FilterOutputFormat.MAC_ADDRESS

    fmd = FilterMetaData()
    fmd.profileId = 0xFF
    fmd.type = FilterType.EXACT_MATCH
    fmd.inputDescription = id
    fmd.outputDescription = od

    return fmd

def exactFilterBlyott():
    exclusionItems = []
    exclusionItems.append([0xcd, 0x09])

    _filterData = ExactMatchFilterData(itemCount=len(exclusionItems), itemSize=len(exclusionItems[0]))
    _filterData.itemArray.val = sum(exclusionItems, [])  # concatenate the items
    return _filterData

def filterBlyott():
    af = AssetFilter()
    af.metadata = getMetaDataBlyott()
    af.filterdata.val = exactFilterBlyott()
    return af

# ----------------- Exact match to exclude filter ----------------------

def getMetaDataExactExclude():
    _input = FilterInputDescription()
    _input.format.type = AdvertisementSubdataType.MAC_ADDRESS

    _output = FilterOutputDescription()
    _output.out_format.type = FilterOutputFormat.MAC_ADDRESS

    _meta = FilterMetaData()
    _meta.profileId = 0
    _meta.type = FilterType.EXACT_MATCH
    _meta.flags = 0b00000001 # last bit indicates 'exclude'
    _meta.inputDescription = _input
    _meta.outputDescription = _output

    return _meta

def exactExcludeFilter():
    exclusionItems = []
    exclusionItems.append([int(x, 16) for x in "60:c0:bf:27:e8:fb".split(":")][::-1])

    _filterData = ExactMatchFilterData(itemCount=len(exclusionItems),itemSize=len(exclusionItems[0]))
    _filterData.itemArray.val = sum(exclusionItems, []) # concatenate the items
    return _filterData

def filterExactExclude():
    _assetFilter = AssetFilter()
    _assetFilter.metadata = getMetaDataExactExclude()
    _assetFilter.filterdata.val = exactExcludeFilter()
    return _assetFilter


# -------------------------
# uart message bus handlers
# -------------------------

def successhandler(*args):
    #print("success handler called", *args)
    pass

def failhandler(*args):
    # print("fail handler called", *args)
    pass

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

def upload(trackingfilter, filterId, max_chunk_size):
    print(" ** starting upload **")
    filter_bytes = trackingfilter.getPacket()
    print("filter bytes: ", filter_bytes)
    data_len = len(filter_bytes)
    print("total filter bytes:", data_len, " filter crc: ", hex(crc32(filter_bytes)), " fitlerid: " , filterId)
    for start_index in range(0, data_len, max_chunk_size):
        end_index = min(start_index + max_chunk_size, data_len)
        print(" -------- Send packet chunk (EVENT) -------- ", start_index,"-", end_index)

        upload_packet = UploadFilterCommandPacket(
            filterId=filterId,
            totalSize=data_len,
            chunkSize=end_index-start_index,
            chunkStartIndex=start_index,
            chunk=filter_bytes[start_index : end_index]
        )

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


def removeAllFilters():
    for i in range(5):
        remove(i)
        time.sleep(0.5)

    return 0x00000000

def uploadFilters():
    # build a few filters
    trackingfilters = []
    # trackingfilters.append(filter0())
    # trackingfilters.append(filter1())
    # trackingfilters.append(filterAlex())
    # trackingfilters.append(filterBlyott())
    # trackingfilters.append(filterExactMacOut())
    trackingfilters.append(filterExactShortIdOut())
    # trackingfilters.append(filterExactExclude())

    # generate filterIds
    masterCrc = AssetFilterUtil.get_master_crc_from_filters(
        [AssetFilterAndId(i, f) for i, f in enumerate(trackingfilters)])

    for f in trackingfilters:
        print("filter crc:", hex(AssetFilterUtil.get_filter_crc(f)))
    print("master crc:", hex(masterCrc))

    # execute some commands
    for i, f in enumerate(trackingfilters):
        print(F"------------- upload filter {i} ---------------");
        upload(f, filterId=i, max_chunk_size=100)
        time.sleep(2)

    print("------------- get summaries ---------------");
    getStatus()
    time.sleep(2)

    return masterCrc

def finalizeFilterUpload(masterCrc):
    print("------------- commit upload ---------------");
    commit(crc=masterCrc, version=1)
    time.sleep(2)
    print("------------- get summaries ---------------");
    getStatus()

if __name__ == "__main__":
    # setup uart stuff
    bluenetLogs = BluenetLogs()
    bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")

    uartfail = UartEventBus.subscribe(SystemTopics.uartWriteError, failhandler)
    uartsucces = UartEventBus.subscribe(SystemTopics.uartWriteSuccess, successhandler)
    uartresult = UartEventBus.subscribe(SystemTopics.resultPacket, resulthandler)

    uart = CrownstoneUart()
    uart.initialize_usb_sync(port='/dev/ttyACM0')
    time.sleep(5)

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