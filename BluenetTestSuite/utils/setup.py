from bluenet_logs import BluenetLogs
from crownstone_uart import CrownstoneUart
import logging

def setupCrownstoneUart():
    """
    Todo: load config file to remove dependency on my local machine.
    """
    uart = CrownstoneUart()
    uart.initialize_usb_sync(port='/dev/ttyACM0')

    return uart

def setupCrownstoneLogs():
    """
    Todo: load config file to remove dependency on my local machine.
    """
    bluenetLogs = BluenetLogs()
    bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")
    return bluenetLogs

def setupLogLevel(info=None, debug=None, warn=None):
    if info:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    elif debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    elif warn:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)


def getMacList() :
    return [
        # '60:c0:bf:28:0d:ae'  # blyott
        'ac:23:3f:71:cd:36' # minew
    ]
