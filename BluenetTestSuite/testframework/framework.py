import unittest

from BluenetTestSuite.firmwarecontrol import *
from BluenetTestSuite.firmwarestate.firmwarestate import *
from BluenetLib import Bluenet
import uuid
from colorama import Fore, Back, Style


# TODO: Convert to unittest library so that tests can be automatically discovered / executed
# E.g.  class TestFramework(unittest.TestCase):

class TestFramework:
    # construction
    def __init__(self, testfunction):
        """
        parameter [testfunction] implements the actual test and should return a
        human readable string that represents the result.
        """
        self.test_impl = testfunction

        # Create new instance of Bluenet
        self.bluenet = Bluenet()
        self.firmwarestate = FirmwareState()

    # __enter__ is part of the 'with' interface. It is used to setup the testframework
    def __enter__(self):
        # def setUp(self):
        connectedport = initializeUSB(self.bluenet, "ttyACM", range(4))

        if connectedport == None:
            print("failed to connect to port in specified range")
            return None
        else:
            # print("connected to " + connectedport)
            pass

        return self

    # __exit__ is part of the 'with' interface. It will be used to tear down the test environment.
    def __exit__(self, type, value, traceback):
        # def tearDown(self):
        self.bluenet.stop()

    @classmethod
    def success(cls, note=""):
        return "{0}Result: Success{1} ({2})".format(Style.BRIGHT + Fore.GREEN, Style.RESET_ALL, note)

    @classmethod
    def failure(cls, cause=""):
        """
        Returns a formatted failure string containing a uuid that is also
        printed during this call so that the failure can be easily be retrieved
        in the logs as well as final output.
        """
        failureid = uuid.uuid4()

        failstr = "{0}Result: Failure ({2}){1}".format(Style.BRIGHT + Fore.RED, Style.RESET_ALL, failureid)

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
        print("Framework test_run time: ", t2-t1)
        return result
