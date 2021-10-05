
# --------- filter 0 --------
# from crownstone_core.packets.assetFilter.FilterIOPackets import *
from crownstone_core.packets.assetFilter.FilterMetaDataPackets import *
from crownstone_core.util.Cuckoofilter import CuckooFilter


from crownstone_core.packets.assetFilter.builders.AssetFilter import AssetFilter, OptimizeOutputStrategy
from crownstone_core.packets.assetFilter.FilterMetaDataPackets import FilterMetaData, FilterType
from crownstone_core.packets.assetFilter.builders.AssetIdSourceBuilder import AssetIdSourceBuilder


#
# def getMetaData0():
#     id = FilterInputDescription()
#     id.format.type = AdvertisementSubdataType.MAC_ADDRESS
#
#     # id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
#     # ffmad = FilterFormatMaskedAdData()
#     # ffmad.adType = 0xdd
#     # ffmad.mask = 0xabcdef12
#     # id.format.format.val = ffmad
#
#     od = FilterOutputDescription()
#     od.out_format.type = FilterOutputFormat.MAC_ADDRESS
#
#     fmd = FilterMetaData()
#     fmd.profileId = 0x00
#     fmd.inputDescription = id
#     fmd.outputDescription = od
#
#     return fmd

def cuckoo0():
    cuckoo = CuckooFilter(3, 2)
    cuckoo.add([0xac, 0x23, 0x3f, 0x71, 0xca, 0x77][::-1]) # D15N minew beacon on my desk
    return cuckoo

# def filter0():
#     af = AssetFilter()
#     af.metadata = getMetaData0()
#     af.filterdata.val = cuckoo0().getData()
#     return af

# --------- filter 1 ------------


# def getMetaData1():
#     id = FilterInputDescription()
#     id.format.type = AdvertisementSubdataType.MAC_ADDRESS
#
#     # id.format.type = AdvertisementSubdataType.AD_DATA
#     # ffad = FilterFormatAdData()
#     # ffad.adType = 0x16 # servicedata
#     # id.format.format.val = ffad
#
#     id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
#     ffmad = FilterFormatMaskedAdData()
#     ffmad.adType = 0x16  # type == servicedata
#     # ffmad.mask = 0xffffffff # mask out 'nothing'
#     ffmad.mask = 0b1111  # mask out only last few bytes
#     id.format.format.val = ffmad
#
#     od = FilterOutputDescription()
#     od.out_format.type = FilterOutputFormat.MAC_ADDRESS
#
#     fmd = FilterMetaData()
#     fmd.profileId = 0x00
#     fmd.inputDescription = id
#     fmd.outputDescription = od
#
#     return fmd

def cuckoo1():
    cuckoo = CuckooFilter(4, 4)
    # service data (type 0x16) content of one of the advertisements that
    # the D15N minew beacon broadcasts.
    # cuckoo.add([0xaa,0xfe,0x10,0xe8,0x01,0x6d,0x69,0x6e,0x65,0x77,0x00])

    # cuckoo.add([0xaa, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # cuckoo.add([0xaa, 0xfe, 0x10,0xe8])
    cuckoo.add([0xaa,0xfe,0x10,0xe8])

    return cuckoo

# def filter1():
#     af = AssetFilter()
#     af.metadata = getMetaData1()
#     af.filterdata.val = cuckoo1().getData()
#     return af




# ------------ Alex' filter -----------


# def getMetaDataAlex():
#     id = FilterInputDescription()
#     id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
#     ffmad = FilterFormatMaskedAdData()
#     ffmad.adType = 0xFF
#     ffmad.mask = 0b11
#     id.format.format.val = ffmad
#
#     od = FilterOutputDescription()
#     od.out_format.type = FilterOutputFormat.MAC_ADDRESS
#
#     fmd = FilterMetaData()
#     fmd.profileId = 0xFF
#     fmd.type = FilterType.EXACT_MATCH
#     fmd.inputDescription = id
#     fmd.outputDescription = od
#
#     return fmd

def cuckooAlex():
    cuckoo = CuckooFilter(0, 2)
    cuckoo.add([0xcd, 0x09])
    # cuckoo.add([0xcd, 0x09][::-1])
    return cuckoo

# def filterAlex():
#     af = AssetFilter()
#     af.metadata = getMetaDataAlex()
#     af.filterdata.val = cuckooAlex().getData()
#     return af




# ----------------- exact match filter ----------------------

def filterExactMacInForwarderMacOut(maclist):
    """
    Returns an AssetFilter for exact matching of the given list of mac addresses.

    Filter output description is of type FilterOutputFormat.MAC_ADDRESS.

    maclist: a list of strings ['60:c0:bf:28:0d:ae'] in human read mac addres.
    Items will be reversed.
    """
    af = AssetFilter()
    af.setProfileId(0)
    af.setFilterType(FilterType.EXACT_MATCH)
    af.filterByMacAddress(maclist)

    af.outputMacRssiReport()

    return af

def filterExactMacInNearestShortIdOut(maclist):
    """
    Returns an AssetFilter for exact matching of the given list of mac addresses.

    Filter output description is of type FilterOutputFormat.SHORT_ASSET_ID.

    maclist: a list of strings ['60:c0:bf:28:0d:ae'] in human read mac addres.
    Items will be reversed.
    """
    af = AssetFilter()
    af.setProfileId(0)
    af.setFilterType(FilterType.EXACT_MATCH)
    af.filterByMacAddress(maclist)
    af.outputAssetId(optimizeStrategy=OptimizeOutputStrategy.NEAREST).basedOnMac() # is this configured correctly now?

    return af

def filterExactMacInForwarderOutputNone(maclist):
    """
    Returns an AssetFilter for exact matching of the given list of mac addresses.

    Filter output description is of type FilterOutputFormat.NONE.

    maclist: a list of strings ['60:c0:bf:28:0d:ae'] in human read mac addres.
    Items will be reversed.
    """
    af = AssetFilter()
    af.setProfileId(0)
    af.setFilterType(FilterType.EXACT_MATCH)
    af.filterByMacAddress(maclist)

    af.outputNone()

    return af


def filterExactMacInForwarderShortIdOut(maclist):
    """
    Returns an AssetFilter for exact matching of the given list of mac addresses.

    Filter output description is of type FilterOutputFormat.SHORT_ASSET_ID.

    maclist: a list of strings ['60:c0:bf:28:0d:ae'] in human read mac addres.
    Items will be reversed.
    """
    af = AssetFilter()
    af.setProfileId(0)
    af.setFilterType(FilterType.EXACT_MATCH)
    af.filterByMacAddress(maclist)
    af.outputAssetId().basedOnMac()

    return af


# def filterBlyott():
#     af = AssetFilter()
#     af.metadata = getMetaDataBlyott()
#     af.filterdata.val = exactFilterBlyott()
#     return af



# ---------------- construction ---------------

# def exactMacFilterData(maclist = [], reverse=True):
#     """
#     Builds exact match filter data object, checking sizes etc.
#     Items should be mac addresses as strings in human readible format.
#     I.e. hex without leading (0x) separated by colons (:).
#     they will be reversed unless specified otherwise.
#     """
#
#     if not maclist:
#         return None
#
#     count = len(maclist)
#     if count == 0:
#         return None
#
#     # transform strings to byte arrays
#     maclist_as_bytes = []
#     if not reverse:
#         for mac in maclist:
#             maclist_as_bytes.append([int(x, 16) for x in mac.split(":")])
#     else:
#         for mac in maclist:
#             maclist_as_bytes.append([int(x, 16) for x in mac.split(":")][::-1])
#
#     size_as_bytes = len(maclist_as_bytes[0])
#     if any([len(mac_as_bytes) != size_as_bytes for mac_as_bytes in maclist_as_bytes]):
#         return None
#
#     # construct filterdata
#     filly = ExactMatchFilterData(itemCount=count, itemSize=size_as_bytes)
#     filly.itemArray.val = sum(maclist_as_bytes, [])
#
#     return filly


# def getMetaDataExactMacOut():
#     id = FilterInputDescription()
#     id.format.type = AdvertisementSubdataType.MAC_ADDRESS
#
#     od = FilterOutputDescription()
#     od.out_format.type = FilterOutputFormat.MAC_ADDRESS
#
#     fmd = FilterMetaData()
#     fmd.profileId = 0x00
#     fmd.type = FilterType.EXACT_MATCH
#     fmd.inputDescription = id
#     fmd.outputDescription = od
#
#     return fmd


# def getMetaDataExactShortIdOut():
#     id = FilterInputDescription()
#     id.format.type = AdvertisementSubdataType.MAC_ADDRESS
#
#     od = FilterOutputDescription()
#     od.out_format = FilterOutputFormat.SHORT_ASSET_ID
#     od.in_format.loadType()
#     od.in_format.val.type = AdvertisementSubdataType.MAC_ADDRESS
#
#     fmd = FilterMetaData()
#     fmd.profileId = 0x00
#     fmd.type = FilterType.EXACT_MATCH
#     fmd.inputDescription = id
#     fmd.outputDescription = od
#
#     return fmd




# ----------------- Exact match to exclude filter ----------------------
#
# def getMetaDataExactExclude():
#     _input = FilterInputDescription()
#     _input.format.type = AdvertisementSubdataType.MAC_ADDRESS
#
#     _output = FilterOutputDescription()
#     _output.out_format.type = FilterOutputFormat.MAC_ADDRESS
#
#     _meta = FilterMetaData()
#     _meta.profileId = 0
#     _meta.type = FilterType.EXACT_MATCH
#     _meta.flags = 0b00000001 # last bit indicates 'exclude'
#     _meta.inputDescription = _input
#     _meta.outputDescription = _output
#
#     return _meta
#
# def exactExcludeFilter():
#     exclusionItems = []
#     exclusionItems.append([int(x, 16) for x in "60:c0:bf:27:e8:fb".split(":")][::-1])
#
#     _filterData = ExactMatchFilterData(itemCount=len(exclusionItems),itemSize=len(exclusionItems[0]))
#     _filterData.itemArray.val = sum(exclusionItems, []) # concatenate the items
#     return _filterData

# def filterExactExclude():
#     _assetFilter = AssetFilter()
#     _assetFilter.metadata = getMetaDataExactExclude()
#     _assetFilter.filterdata.val = exactExcludeFilter()
#     return _assetFilter
#


# ------------ Blyott filter -----------

#
# def getMetaDataBlyott():
#     id = FilterInputDescription()
#     id.format.type = AdvertisementSubdataType.MASKED_AD_DATA
#     ffmad = FilterFormatMaskedAdData()
#     ffmad.adType = 0xFF
#     ffmad.mask = 0b11
#     id.format.format.val = ffmad
#
#     od = FilterOutputDescription()
#     od.out_format.type = FilterOutputFormat.MAC_ADDRESS
#
#     fmd = FilterMetaData()
#     fmd.profileId = 0xFF
#     fmd.type = FilterType.EXACT_MATCH
#     fmd.inputDescription = id
#     fmd.outputDescription = od
#
#     return fmd
#
# def exactFilterBlyott():
#     exclusionItems = []
#     exclusionItems.append([0xcd, 0x09])
#
#     _filterData = ExactMatchFilterData(itemCount=len(exclusionItems), itemSize=len(exclusionItems[0]))
#     _filterData.itemArray.val = sum(exclusionItems, [])  # concatenate the items
#     return _filterData


if __name__ == "__main__":
    # if invoked stand alone, just call all generators once to see if there are any silly import bugs etc.
    # getMetaData0()
    cuckoo0()
    # filter0()
    # getMetaData1()
    cuckoo1()
    # filter1()
    # getMetaDataAlex()
    cuckooAlex()
    # filterAlex()

    maclist = ['60:c0:bf:28:0d:ae']
    filterExactMacInForwarderMacOut(maclist)
    filterExactMacInNearestShortIdOut(maclist)
    filterExactMacInForwarderOutputNone(maclist)
    filterExactMacInForwarderShortIdOut(maclist)
