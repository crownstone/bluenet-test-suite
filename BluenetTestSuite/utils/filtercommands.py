import time

from crownstone_core.packets.assetFilter.FilterCommandPackets import *
from crownstone_core.packets.assetFilter.util.AssetFilterMasterCrc import get_master_crc_from_filters
from crownstone_core.protocol.BluenetTypes import ControlType
from crownstone_core.util.CRC import crc32
from crownstone_core.packets.assetFilter.util import *

from BluenetTestSuite.firmwarecontrol.datatransport import sendCommandToCrownstone


def getStatus():
    sendCommandToCrownstone(ControlType.ASSET_FILTER_GET_SUMMARIES, [])


def removeAllFilters():
    for i in range(5):
        remove(i)
        time.sleep(0.5)

    return 0x00000000

def uploadFilters(trackingfilters):
    """
    trackingFilter: List[AssetFilter]

    E.g.
    trackingfilters = []
    trackingfilters.append(filter0())
    trackingfilters.append(filter1())
    trackingfilters.append(filterAlex())
    trackingfilters.append(filterBlyott())
    trackingfilters.append(filterExactMacOut())
    trackingfilters.append(filterExactMacInShortIdOut())
    trackingfilters.append(filterExactExclude())
    """
    # generate filterIds
    masterCrc = get_master_crc_from_filters(trackingfilters)

    for i, f in enumerate(trackingfilters):
        print(F"------------- upload filter {i} ---------------");
        upload(f, filterId=i, max_chunk_size=100)
        time.sleep(2)

    print("------------- get summaries ---------------");
    getStatus()
    time.sleep(2)

    return masterCrc

def finalizeFilterUpload(masterCrc, version=1):
    print("------------- commit upload ---------------");
    commit(crc=masterCrc, version=version)
    time.sleep(2)
    print("------------- get summaries ---------------");
    getStatus()


# ----------------------- lower level commands -----------------------

def upload(trackingfilter, filterId, max_chunk_size):
    print(" ** starting upload **")
    filter_bytes = trackingfilter.serialize()
    print("filter bytes: ", filter_bytes)
    data_len = len(filter_bytes)
    print("total filter bytes:", data_len, " filter crc: ", hex(crc32(filter_bytes)), " fitlerid: " , filterId)
    for start_index in range(0, data_len, max_chunk_size):
        end_index = min(start_index + max_chunk_size, data_len)
        print(" -------- Send packet chunk (EVENT) -------- ", start_index,"-", end_index)

        upload_packet = UploadFilterChunkPacket(
            filterId=filterId,
            totalSize=data_len,
            chunkSize=end_index-start_index,
            chunkStartIndex=start_index,
            chunk=filter_bytes[start_index : end_index]
        )

        sendCommandToCrownstone(ControlType.ASSET_FILTER_UPLOAD, upload_packet.serialize())
        time.sleep(0.5)


def remove(filterId):
    removePacket = RemoveFilterPacket(filterId)
    sendCommandToCrownstone(ControlType.ASSET_FILTER_REMOVE, removePacket.serialize())

def commit(crc, version):
    commitCommand = CommitFilterChangesPacket(masterCrc=crc, masterVersion=version)
    sendCommandToCrownstone(ControlType.ASSET_FILTER_COMMIT_CHANGES, commitCommand.serialize())
