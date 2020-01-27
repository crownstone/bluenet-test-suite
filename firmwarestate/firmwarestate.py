import time, inspect, sys
from BluenetLib import Bluenet, BluenetEventBus, UsbTopics

from BluenetLib.lib.core.uart.UartTypes import UartRxType
from BluenetLib.lib.topics.SystemTopics import SystemTopics

import pprint
import pygame #for nice keyboard input

class FirmwareState:
    """
    Listens to UART over a port and keeps track of any state values logged by the firmware.
    """
    def __init__(self):
        BluenetEventBus.subscribe(SystemTopics.uartNewPackage, self.parse)
        # statedict: dict (int -> dict (string -> value) ),
        # thisptr -> valuename -> value
        self.statedict = dict()

    def clear(self):
        """
        Clears the state dict.
        """
        self.statedict.clear()

    def parse(self, dataPacket):
        """
        Parses a message from crownstone.
        """
        opCode = dataPacket.opCode
        if opCode == UartRxType.FIRMWARESTATE:
            stringResult = ""
            for byte in dataPacket.payload:
                if byte < 128:
                    stringResult += chr(byte)
            statelist = stringResult.split(",")

            self.pushvalue("0x"+statelist[0], statelist[1], statelist[2], statelist[3])

    def construct(self, ptr, typename):
        """
        Appends [typename] to self.statedict[ptr]["typename."].
        """
        if ptr not in self.statedict:
            self.statedict[ptr] = dict()
            self.statedict[ptr]["typename"] = ""
        self.statedict[ptr]["typename"] += typename

    def destruct(self, ptr):
        """
        Removes the object with address [ptr] from [self.statedict]
        """
        self.statedict.pop(ptr, None)

    def pushvalue(self, ptr, scopename, valuename, value):
        """
        Add or update value in the state dict. If ptr wasn't contained in it yet, adds an entry
        """
        if ptr not in self.statedict:
            classname = ""
            try:
                # try to infer class name from gnu __PRETTY_FUNCTION__ (impl dependent).
                # it should be the last cpp token of the top-most level scoped part in the string
                # (note: assumes our code is in global namespace.)
                # (note: it's not possible to distinguish this from top-level function names.)
                classname = scopename.split("::")[0].split(" ")[-1]
            except Exception as inst:
                # the exception instance
                print("couldn't identify classname: " + type(inst) + " " + scopename)
                pass
            self.construct(ptr, classname)

        self.statedict[ptr][valuename] = value

def initializeUSB(bluenet_instance, portname, a_range):
    """
    Tries to connect to the given busname with the given index. If it finds one it will break,
    logs where there is none. And returns full connected port name as string on success/None object on failure.
    """
    for i in a_range:
        try:
            port = "/dev/{0}{1}".format(portname,i)
            bluenet_instance.initializeUSB(port)
            return port
        except Exception as err:
            print("coudn't find '/dev/ttyACM{0}', trying next port".format(i))
            print(err)
    return None

class Main:
    """
    If this file is run as stand alone script, it will output the current state of the firmware.
    """
    def __init__(self):
        # Create new instance of Bluenet
        self.bluenet = Bluenet()

        # create FirmwareState instance - this must be constructed after Bluenet().
        self.fwState = FirmwareState()

        # see if we can find a crownstone on one of the ACM busses
        # note: this is where we could add several FirmwareState objects
        # (1 per uart bus) whenever we wish to write tests involving several crownstones,
        # each of them on their own j-link.
        initializeUSB(self.bluenet, "ttyACM", range(4))

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

        prettyprinter = pprint.PrettyPrinter(indent=4)
        prettyprint = prettyprinter.pprint
        run = True
        while run:
            pygame.time.delay(100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == ord(' '):
                        prettyprint(self.fwState.statedict)

if __name__ == "__main__":
    with Main() as m:
        m.run()