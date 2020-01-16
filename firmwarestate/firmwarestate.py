import time, inspect, sys
from BluenetLib import Bluenet, BluenetEventBus, UsbTopics

from BluenetLib.lib.core.uart.UartTypes import UartRxType
from BluenetLib.lib.core.uart.UartTypes import UartTxType
from BluenetLib.lib.core.uart.UartWrapper import UartWrapper
from BluenetLib.lib.core.uart.uartPackets import UartPacket
from BluenetLib.lib.protocol.BlePackets import ControlPacket
from BluenetLib.lib.protocol.BluenetTypes import ControlType
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.util.Conversion import Conversion

import pygame #for nice keyboard input

# def sendToCrownstone(commandtype, packetcontent):
#     controlPacket = ControlPacket(commandtype)
#     controlPacket.appendByteArray(packetcontent)

#     uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket.getPacket()).getPacket()
    
#     BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)

# def propagateEventToCrownstone(eventtype, eventdata):
#     payload = []
#     payload += Conversion.uint16_to_uint8_array(eventtype)
#     payload += eventdata
    
#     uartPacket = UartWrapper(UartTxType.MOCK_INTERNAL_EVT,payload).getPacket()
#     BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)


class FirmwareState:
    """
    Listens to UART over a port and keeps track of any state values logged by the firmware.
    """
    def __init__(self):
        BluenetEventBus.subscribe(SystemTopics.uartNewPackage, self.parse)

    def parse(self, dataPacket):
        opCode = dataPacket.opCode
        if opCode == UartRxType.FIRMWARESTATE:
            stringResult = ""
            for byte in dataPacket.payload:
                if byte < 128:
                    stringResult += chr(byte)
            logStr = "FW update: %15.3f - %s" % (time.time(), stringResult)
            sys.stdout.write(logStr)


class Main:
    """
    If this file is run as stand alone script, it will output the current state of the firmware.
    """
    #construction
    def __init__(self):
        # Create new instance of Bluenet
        self.bluenet = Bluenet()
        self.fwState = FirmwareState()

        # see if we can find a crownstone on one of the ACM busses
        # note: this is where we could add several FirmwareState objects
        # (1 per uart bus) whenever we wish to write tests involving several crownstones,
        # each of them on their own j-link.
        for i in range(4):
            try:
                self.bluenet.initializeUSB("/dev/ttyACM{0}".format(i))
                break
            except:
                print("coudn't find /dev/ttyACM{0}, trying next port".format(i))

        pygame.init()
        self.window = pygame.display.set_mode((400,400))
    
    # implements 'with' interface to enforce timely destruction even when Bluenet wants
    # to stay alive.
    def __enter__(self):
        # Set up event listeners
            return self
    
    def __exit__(self, type, value, traceback):
        print("goodbye cruel world")
        pygame.quit()
        # BluenetEventBus.unsubscribe(self.subscriptionId)
        self.bluenet.stop()

    def run(self):
        print("firmwarestate up and running")

        run = True
        while run:
            pygame.time.delay(100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

if __name__ == "__main__":
    with Main() as m:
        m.run()