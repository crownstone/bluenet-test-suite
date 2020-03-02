import unittest

from firmwarecontrol import *
from firmwarestate.firmwarestate import *
from BluenetLib import Bluenet
import uuid


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
    def success(cls):
        return "Result: Success"

    @classmethod
    def failure(cls, cause=""):
        """
        Returns a formatted failure string containing a uuid that is also
        printed during this call so that the failure can be easily be retrieved
        in the logs as well as final output.
        """
        failureid = uuid.uuid4()
        print("Failure({0}) reported".format(failureid))

        if cause:
            return "Result: Failure ({0}): ".format(failureid) + cause
        return "Result: Failure ({0})".format(failureid)

    def test_run(self):
        """
        Runs the testfunction which this instance was constructed with and prints its result.
        """
        print(self.test_impl(self.firmwarestate))
