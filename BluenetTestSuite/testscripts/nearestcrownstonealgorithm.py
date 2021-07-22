"""
This script monitors the conclusions that the NearestCrownstoneAlgorithm makes:

A list of assets is defined.
Two filters are constructed, which both represent the list of assets.
The filters are identical, except for the output type, which is MAC resp. SID.
The filters are commited into the mesh.
The SIDs are constructed for this list of assets and a map SID -> index in asset list is constructed.

From that point on, the crownstone that is connected via UART will provide the events:
- 10108: Asset Rssi Data
- 10109: Nearest Crownstone Update
- 10110: Nearest Crownstone TimeOut

These incoming events are linked to the original list of assets by their index and they are timestamped.
At each incoming event, the status can be validated:
- If a Nearest Crownstone Update is received, does it match with the Nearest Crownstone
  according to the Asset Rssi Data events?
  (Possibly allowing accomodation time and rssi margin)
- If a Nearest Crownstone TimeOut is received, how long ago was the last Asset Rssi Data event?


All of this can be displayed in a rolling graph by simply plotting per asset the time series of each crownstones
rssi values received through the Asset Rssi Data events and annotating the winner transitions and timeouts etc.
- winner: think line
- timed out: dotted/dashed
- other: normal line

"""
import time
# import logging
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


import crownstone_uart
from crownstone_uart import CrownstoneUart, UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket
from crownstone_uart.core.uart.UartTypes import UartRxType
from crownstone_uart.core.uart.uartPackets.NearestCrownstones import NearestCrownstoneTrackingUpdate, NearestCrownstoneTrackingTimeout
from crownstone_uart.core.uart.uartPackets.AssetMacReport import AssetMacReport

from bluenet_logs import BluenetLogs

# data format definitions for plotting and managing state.

class WinnerChangedEvent:
    """
    Plotting data for the winner state according to the incoming uart data.
    """
    nextWinnerId = None
    timestamp = None

class ErrorState:
    """
    Plotting data for any possible error states according to this scripts conclusions. May be 'OK', 'WRONG_WINNER', etc..
    """
    timestamp = None
    errorstate = None

class AssetValidEvent:
    """
    Record of a change in validity of an rssi stream. E.g. when a timeout occurs.
    """
    timestamp = None
    nextIsValidState = None

class RssiStream:
    """
    Plotting data for a rssi time series between a particular pair of bluetooth devices.
    """
    rssiQ = None  # measured
    validQ = None  # measured: queue of AssetValidEvent

class AssetPlottingData:
    """
    Plotting data for a particular asset. Contains rssi time series for each crownstone that hears it.
    """
    filterdata = None
    Sid = None # generated
    winnerStateQ = None  # measured: queue of WinnerChangedEvents
    errorStateQ = None  # measured: queue of ErrorStates
    crownstoneStreams = None

class PlottingData:
    """
    All the data that is relevant to visualize a range of assets in a sphere.
    """
    Assets = {sid0: AssetPlottingData(), sid1: AssetPlottingData(), }



# The assest that this script is monitoring during the test.

_assets = [
    Asset(filterdata = [0xac, 0x23, 0x3f, 0x71, 0xca, 0x77][::-1]),
    # ...
]



# Setup of the test

def getAssetList():
    return [0, 1]

def getFilters(assetList):
    pass

def uploadFilters(filters):
    pass

def plot():
    pass

def handleAssetRssiData(msg):
    print("handleAssetRssiData")
    print(msg)

def handleNearestCrownstoneUpdate(msg):
    print("handleNearestCrownstoneUpdate")
    print(msg)

def handleNearestCrownstoneTimeOut(msg):
    print("handleNearestCrownstoneTimeOut")
    print(msg)


def uartmsghandler(msg: UartMessagePacket):
    print(f"Received {str(msg.opCode)}: {msg.payload}")
    if msg.opCode == UartRxType.NEAREST_CROWNSTONE_TRACKING_UPDATE:
        packet = NearestCrownstoneTrackingUpdate()
        packet.setPacket(msg.payload)
        handleNearestCrownstoneUpdate(packet)
    elif msg.opCode == UartRxType.NEAREST_CROWNSTONE_TRACKING_TIMEOUT:
        packet = NearestCrownstoneTrackingTimeout()
        packet.setPacket(msg.payload)
        handleNearestCrownstoneTimeOut(packet)
    elif msg.opCode == UartRxType.ASSET_MAC_RSSI_REPORT:
        packet = AssetMacReport()
        packet.setPacket(msg.payload)
        handleAssetRssiData(packet)



if __name__ == "__main__":
    # setup uart stuff
    bluenetLogs = BluenetLogs()
    bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")

    uartmsgs = UartEventBus.subscribe(SystemTopics.uartNewMessage, uartmsghandler)

    uart = CrownstoneUart()
    uart.initialize_usb_sync(port='/dev/ttyACM0')
    time.sleep(5)

    assetList = getAssetList()
    filters = getFilters(assetList)

    uploadFilters(filters)

    # let it run for a bit
    try:
        while True:
            time.sleep(1)
            print(" * script still running * ")
            plot()
    except:
        print("escaped while loop")

    uart.stop()