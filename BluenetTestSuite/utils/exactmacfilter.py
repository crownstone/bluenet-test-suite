from crownstone_core.packets.assetFilter.builders.AssetFilter import AssetFilter
from crownstone_core.packets.assetFilter.FilterMetaDataPackets import FilterMetaData, FilterType


# ----------------- exact match filter ----------------------
from crownstone_core.packets.assetFilter.builders.AssetIdSourceBuilder import AssetIdSourceBuilder


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
    af.filterByMacAddress(['60:c0:bf:28:0d:ae'])

    af.outputForwardRssiReport()

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
    af.filterByMacAddress(['60:c0:bf:28:0d:ae'])
    af.outputAssetIdFromNearest().basedOnMac()

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
    af.filterByMacAddress(['60:c0:bf:28:0d:ae'])
    af.outputForwardRssiReport(useAssetId=True).basedOnMac()

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


