# import unittest
import uuid
from colorama import Fore, Back, Style
import logging
import os, sys

from bluenet_logs import BluenetLogs
from crownstone_uart import CrownstoneUart

from BluenetTestSuite.firmwarestate.firmwarestate import *


# TODO: Convert to unittest or pytest library so that tests can be automatically discovered / executed
# E.g.  class TestFramework(unittest.TestCase):

class TestFramework:
    """
    Small framework to run and report results of tests. Construct with a test function in a
    with-as statement for automatic uart initialization and disconnection.

    """
    # construction
    def __init__(self, testfunction):
        """
        parameter [testfunction] implements the actual test.
        It must accept a single parameter of type FirmwareState and return a
        human readable string that represents the result.
        """
        self.test_impl = testfunction

        # Create the uart connection
        self.bluenetLogs = BluenetLogs()
        self.bluenetLogs.setSourceFilesDir("/home/arend/Documents/crownstone-bluenet/bluenet/source")
        self.uart = CrownstoneUart()
        self.firmwarestate = FirmwareState()

    # __enter__ is part of the 'with' interface. It is used to setup the testframework
    def __enter__(self):
        self.uart.initialize_usb_sync(port='/dev/ttyACM0')
        return self

    # __exit__ is part of the 'with' interface. It will be used to tear down the test environment.
    def __exit__(self, type, value, traceback):
        self.uart.stop()
        pass

    @classmethod
    def success(cls, note=""):
        return "{0}Result: Success{1} ({2})".format(Style.BRIGHT + Fore.GREEN, Style.RESET_ALL, note)

    @classmethod
    def failure(cls, cause=None):
        """
        Returns a formatted failure string containing a uuid that is also
        printed during this call so that the failure can be easily be retrieved
        in the logs as well as final output.
        """
        failureid = ""
        if cause is None:
            failureid = "({0})".format(uuid.uuid4())

        failstr = "{0}Result: Failure {2}{1}".format(Style.BRIGHT + Fore.RED, Style.RESET_ALL, failureid)

        if cause:
            failstr += ": " + cause

        print (failstr)
        return failstr

    def test_run(self):
        """
        Runs the testfunction which this instance was constructed with and returns its result.
        """
        t1 = time.time()
        result = self.test_impl(self.firmwarestate)
        t2 = time.time()
        print("========================================================================")
        print("Main python file: ", os.path.basename(sys.argv[0]))
        print("Framework test_run time: {0:.3f}".format(t2-t1))
        print("========================================================================")
        return result
