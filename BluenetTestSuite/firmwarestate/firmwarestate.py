import time, inspect, sys

import datetime
import pprint
from colorama import Fore, Style

from bluenet_logs import BluenetLogs
from crownstone_uart import CrownstoneUart
from crownstone_uart.core.UartEventBus import UartEventBus
from crownstone_uart.core.uart.UartTypes import UartRxType
from crownstone_uart.topics.SystemTopics import SystemTopics


from BluenetTestSuite.firmwarestate.firmwarestatehistoryentry import FirmwareStateHistoryEntry

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

class FirmwareState:
    """
    Listens to UART over a port and keeps track of any state values logged by the firmware.
    """
    def __init__(self):
        self.uartSubscription = UartEventBus.subscribe(SystemTopics.uartNewMessage, self.parse)

        # statedict: dict (int -> dict (string -> value) ),
        # thisptr -> valuename -> value
        self.statedict = dict()
        self.historylist = []

        # list of callbacks taking one firmwarestatehistoryentry as parameter
        self.onNewEntryParsed = []

    def clear(self):
        """
        Clears the state dict.
        """
        self.statedict.clear()
        self.historylist.clear()

    def classnamefromprettyfunction(self, prettyfunctionname):
        classname = ""
        try:
            # try to infer class name from gnu __PRETTY_FUNCTION__ (impl dependent).
            # it should be the last cpp token of the top-most level scoped part in the string
            # (note: assumes our code is in global namespace.)
            # (note: it's not possible to distinguish this from top-level function names.)
            classname = prettyfunctionname.split("::")[0].split(" ")[-1]
        except Exception as inst:
            # the exception instance
            print("couldn't identify classname: " + type(inst) + " " + prettyfunctionname)
            pass
        return classname

    def parse(self, dataPacket):
        """
        Parses a message from crownstone of type UartRxType.FIRMWARESTATE, and calls the installed callbacks
        in self.onNewEntryParsed
        """
        opCode = dataPacket.opCode
        if opCode == UartRxType.FIRMWARESTATE:
            stringResult = ""
            for byte in dataPacket.payload:
                if byte < 128:
                    stringResult += chr(byte)

            print("{0}firmware state update: {2}{1}".format(Fore.LIGHTBLACK_EX,Style.RESET_ALL,stringResult))
            statelist = stringResult.split("@")

            try:
                statelist[1] = self.classnamefromprettyfunction(statelist[1])
            except:
                print(stringResult)

            self.pushstatevalue("0x" + statelist[0], statelist[1], statelist[2], statelist[3])
            self.pushhistoryvalue("0x" + statelist[0], statelist[1], statelist[2], statelist[3])

            for callback in self.onNewEntryParsed:
                callback(self.historylist[-1])

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

    def pushstatevalue(self, ptr, classname, valuename, value):
        """
        Add or update value in the state dict. If ptr wasn't contained in it yet, adds an entry
        """
        if ptr not in self.statedict:
            self.construct(ptr, classname)

        self.statedict[ptr][valuename] = value

    def pushhistoryvalue(self, ptr, classname, valuename, value):
        """
        Adds a record to the historylist.
        """
        self.historylist += [FirmwareStateHistoryEntry(
            datetime.datetime.now(), ptr, classname, valuename, value)]

    def printhistory(self):
        prettyprinter = pprint.PrettyPrinter(indent=4)
        prettyprint = prettyprinter.pprint
        prettyprint(self.historylist)

    def print(self):
        prettyprinter = pprint.PrettyPrinter(indent=4)
        prettyprint = prettyprinter.pprint
        prettyprint(self.statedict)

    def getValue(self, classname, expressionname):
        for ptr, obj in self.statedict.items():
            if obj.get('typename') == classname:
                return obj.get(expressionname)
        return None

    def getValues(self, classname, expressionname):
        result = []
        for ptr, obj in self.statedict.items():
            if obj.get('typename') == classname:
                value = obj.get(expressionname)
                if value is not None:
                    result += [value]
        return result

    def assertFindFailuresMulti(self, classname, expressionname, values):
        """
        Checks if for all objects of type [classname] the entry for [expressionname] a value in [values].

        Returns a list of pointers (keys in the statedict) to objects that fail this test, including:
            - those entries which do not contain given variablename
            - those entries which dissatisfy containment test.
        Returns None if no objects of given classname where found.

        Note: value will be stringified.
        """
        failures = []
        strvalues = [str(value) for value in values]
        existsAny = False
        for ptr, obj in self.statedict.items():
            if obj.get('typename') == classname:
                existsAny = True
                if obj.get(expressionname) not in strvalues:
                    failures += [ptr]
        if existsAny:
            return failures
        return None

    def assertFindFailures(self, classname, expressionname, value):
        return self.assertFindFailuresMulti(classname, expressionname, [value])

class Main:
    """
    If this file is run as stand alone script, it will output the current state of the firmware.
    """
    def __init__(self):
        # Create the uart connection
        self.uart = CrownstoneUart()
        self.uart.initialize_usb_sync(port="/dev/ttyACM0")

        # create FirmwareState instance - this must be constructed after Bluenet().
        self.bluenetLogs = BluenetLogs()
        self.bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")
        self.fwState = FirmwareState()

        pygame.init()
        self.window = pygame.display.set_mode((400,400))
    
    # implements 'with' interface to enforce timely destruction even when Bluenet wants
    # to stay alive.
    def __enter__(self):
        return self
    
    def __exit__(self, typ, value, traceback):
        pygame.quit()
        self.uart.stop()

    def run(self):
        print("firmwarestate up and running")
        run = True
        while run:
            pygame.time.delay(100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == ord(' '):
                        print("current firmware state:")
                        self.fwState.print()
                    if event.key == ord('h'):
                        self.fwState.printhistory()
                    if event.key == ord('q')  or event.key == ord('Q') or event.key == pygame.K_ESCAPE:
                        run = False


if __name__ == "__main__":
    import pygame  # used for nice keyboard input when used as stand alone script
    with Main() as m:
        m.run()
    print("exiting firmwarestate inspector")
