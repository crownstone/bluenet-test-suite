from BluenetTestSuite.firmwarecontrol.datatransport import sendCommandToCrownstone
from crownstone_core.packets.TrackableParser.TrackableParserPackets import *
from crownstone_core.util.cuckoofilter import *

my_filter = CuckooFilter(8, 2)

some_element = [i % 0x100 for i in range(10)]
my_filter.add(some_element)
print("filter size: " , my_filter.size())
print(my_filter.contains(some_element))

filter_data = TrackingFilterData()
filter_data.metadata.protocol = 1
filter_data.metadata.version = 45
filter_data.metadata.profileId = 0
filter_data.metadata.inputType = FilterInputType.MacAddress
filter_data.metadata.flags = 0x00
filter_data.filter = CuckooPacket(my_filter)

print("metadata", len(filter_data.metadata.getPacket()), filter_data.metadata.getPacket())
print("filter  ", len(filter_data.filter.getPacket()), filter_data.filter.getPacket())
print("combined", len(filter_data.getPacket()), filter_data.getPacket())

print("---------------------------------")
print("generating chunk packets")

raw_filter_data = filter_data.getPacket()
max_chunk_size = 10
data_len = len(raw_filter_data)

for start_index in range(0, data_len, max_chunk_size):
    end_index = min (start_index + max_chunk_size, data_len)

    upload_packet = TrackingFilterUpload()
    upload_packet.filterId = 1
    upload_packet.totalSize = data_len
    upload_packet.chunkSize = end_index - start_index
    upload_packet.chunkStartIndex = start_index
    upload_packet.chunk = raw_filter_data[start_index : end_index]
    print(upload_packet.getPacket())

    # sendCommandtoCrownstone(ControlType.TRACKING_FILTER_UPLOAD, upload_packet.getPacket())