from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType

"""
Mock script that injects a bundle of tracked devices into a crownstone.
"""

# struct __attribute__((packed)) internal_register_tracked_device_packet_t {
# 	register_tracked_device_packet_t data;
# 	uint8_t accessLevel = NOT_SET;
# };

# #define TRACKED_DEVICE_TOKEN_SIZE 3

# struct __attribute__((packed)) register_tracked_device_packet_t {
# 	uint16_t deviceId;
# 	uint8_t locationId = 0;
# 	uint8_t profileId;
# 	int8_t rssiOffset = 0;
# 	union __attribute__((packed)) {
# 		struct __attribute__((packed)) {
# 			bool reserved : 1;
# 			bool ignoreForBehaviour : 1;
# 			bool tapToToggle : 1;
# 		} flags;
# 		uint8_t asInt;
# 	} flags;
# //	uint8_t flags;
# 	uint8_t deviceToken[TRACKED_DEVICE_TOKEN_SIZE];
# 	uint16_t timeToLiveMinutes = 0;
# };

def tracked_dev_packet(deviceId, profileId, locationId, rssiOffset,
                       flags, deviceToken, timeToLiveMinute):
    ret = []
    ret += Conversion.uint16_to_uint8_array(deviceId)
    ret += Conversion.uint8_to_uint8_array(locationId)
    ret += Conversion.uint8_to_uint8_array(profileId)
    ret += Conversion.uint8_to_uint8_array(rssiOffset)
    ret += Conversion.uint8_to_uint8_array(flags)
    ret += deviceToken
    ret += Conversion.uint16_to_uint8_array(timeToLiveMinute)
    return ret


def injectTrackedDevices(FW):
    sendCommandToCrownstone(ControlType.RESET, [])
    time.sleep(10)

    sendCommandToCrownstone(ControlType.REGISTER_TRACKED_DEVICE,
                            tracked_dev_packet(0xaeae, 1, 0, -65, 0b100, [0xa, 0xe, 0xa], 5))
    time.sleep(0.5)

    sendCommandToCrownstone(ControlType.REGISTER_TRACKED_DEVICE,
                            tracked_dev_packet(0x1234, 2, 0, -65, 0b100, [0x1, 0x2, 0x3], 5))
    time.sleep(0.5)

    sendCommandToCrownstone(ControlType.REGISTER_TRACKED_DEVICE,
                            tracked_dev_packet(0xabcd, 3, 0, -65, 0b100, [0xa, 0xb, 0xc], 5))

    input("press enter to quit")

    return TestFramework.success()

if __name__ == "__main__":
    with TestFramework(injectTrackedDevices) as frame:
        if frame != None:
            print(frame.test_run())
        else:
            print(TestFramework.failure())
