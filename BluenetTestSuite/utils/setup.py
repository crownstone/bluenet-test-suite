from bluenet_logs import BluenetLogs
from crownstone_uart import CrownstoneUart

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