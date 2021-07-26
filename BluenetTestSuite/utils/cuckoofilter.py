
# --------- filter 0 --------
from crownstone_core.packets.assetFilter.FilterIOPackets import *
from crownstone_core.packets.assetFilter.FilterMetaDataPackets import *
from crownstone_core.util.Cuckoofilter import CuckooFilter


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
    fmd.profileId = 0x00
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
    fmd.profileId = 0x00
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



