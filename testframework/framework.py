import unittest

from firmwarecontrol import *
from firmwarestate.firmwarestate import *
from BluenetLib import Bluenet

# class TestFramework(unittest.TestCase):
class TestFramework:
    # construction
    def __init__(self, testfunction):
        """
        testfunction implements the actual test and should return a human readable string that represents the result.
        """
        # super(TestFramework,self).__init__()
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

    def testme(self):
        print (self.test_impl(self.firmwarestate))