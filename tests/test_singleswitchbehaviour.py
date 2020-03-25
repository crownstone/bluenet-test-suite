"""
All tests that concern a single switch behaviour.
"""

import time

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType
from BluenetLib.lib.packets.behaviour.Behaviour import *


def buildSwitchBehaviour(from_hours, to_hours, intensity):
    switchbehaviour = Behaviour()
    switchbehaviour.setTimeFrom(from_hours % 24, 0)
    switchbehaviour.setTimeTo(to_hours % 24, 0)
    switchbehaviour.setDimPercentage(intensity)
    return switchbehaviour


def sendBehaviour(index, behaviour):
    packet = behaviour.getPacket()
    sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [index] + behaviour.getPacket())


def sendSwitchCommand(intensity):
    sendCommandToCrownstone(ControlType.SWITCH, [intensity])
    time.sleep(0.5)

def sendSwitchCraftCommand():
    sendEventToCrownstone(0x100 + 20 + 2, [])
    time.sleep(0.5)

class TestCase:
    TestCaseCounter = 0

    def __init__(self, t0, t1, e):
        """
        Two overlapping twilights, such that 't0.from <= t1.from' should intuitively hold.
        The e values express the expected values for the time slots given below. (should be a length 3 list)

                f0           f1       u0           u1
        t0:     |------------|--------|            |
        t1:     |            |--------|------------|
                |    e[0]    |  e[1]  |    e[2]    |

        e[0] should hold at time (f0+f1)/2, which is ex_time(0)
        e[1] should hold at time (f1+u0)/2, which is ex_time(1)
        e[2] should hold at time (u0+u1)/2. which is ex_time(2)
        """
        self.t0 = t0
        self.t1 = t1
        self.e = e
        self.id = __class__.TestCaseCounter
        __class__.TestCaseCounter += 1

    def ex_time(self, index):
        """
        Get the time of day between two expected values
        """

        f0 = self.t0.fromTime.offset
        f1 = self.t1.fromTime.offset
        u0 = self.t0.untilTime.offset
        u1 = self.t1.untilTime.offset

        # lift the intervals from Z/(24*3600)Z to the natural number line
        if u0 < f0:
            u0 += 24*3600

        if u1 < f1:
            u1 += 24*3600

        # check if the intervals intersect on the natural numberline, if not, add a day to the lowest interval.
        if not max(f0,f1) <= min(u0,u1):
            # intersection is empty, move up lower one.
            if f0 <= f1:
                # can check on only one bound because knowledge of intersection
                f0 += 24*3600
                u0 += 24*3600
            else:
                f1 += 24*3600
                u1 += 24*3600

        times_list = sorted([f0, f1, u0, u1])
        # if it's not solved now, I've tried...

        # returns average of two consecutive bounds of the two intervals,
        # wrapping back to Z/(24*3600)Z
        return int((times_list[index] + times_list[index + 1]) / 2.0) % (24*3600)

    def __str__(self):
        return "case {9}: t0=[{0}:00,{1}:00] @{2} t1=[{3}:00,{4}:00], @{5} expect [{6},{7},{8}]".format(
            self.t0.fromTime.offset // 3600, self.t0.untilTime.offset // 3600, self.t0.intensity,
            self.t1.fromTime.offset // 3600, self.t1.untilTime.offset // 3600, self.t1.intensity,
            self.e[0], self.e[1], self.e[2], self.id
        )

    def print(self):
        print(str(self))


def test_loopbody(FW, testcase):
    """
    Test will assume a clean behaviour store, except for possibly index 0 and 1,
    which will be overwritten by the current test case twilights.
    It also assumes that dimming is allowed and the dimmer has started.
    """
    print("##### setup test_twilightconflictresolution_loopbody #####")
    testcase.print()

    # send twilights to behaviour store
    sendBehaviour(0, testcase.t0)
    time.sleep(0.2)
    sendBehaviour(1, testcase.t1)
    time.sleep(0.2)

    # print("reset firmwarestate recorder")

    for i in range(3):
        FW.clear()
        testtime = testcase.ex_time(i)
        sendCommandToCrownstone(ControlType.SET_TIME,
                                Conversion.uint32_to_uint8_array(testtime))
        # sometimes when i == 0, the interval will be empty.
        # in that case the expected values e[0] and e[1] should be equal anyway so
        # it shouldn't make a difference if the sleep(1) will cross interval boundary.
        # we need the second however because I'm not sure if switchAggregator will
        # immediately recompute state upon a setTime event.
        time.sleep(1.5)

        failures = FW.assertFindFailures("TwilightHandler", 'previousIntendedState', testcase.e[i])
        if failures:
            actualvalue = None
            try:
                actualvalue = FW.statedict[failures[0]].get("previousIntendedState")
            except:
                actualvalue = "<not found>"

            failmsg = TestFramework.failure("failed: ({0},{1}). At time: {2}:{3} expected {4} but got {5}".format(
                i, str(testcase), testtime//3600, (testtime % 3600)//60, testcase.e[i], actualvalue))
            testcase.print()
            FW.print()
            return failmsg

    return TestFramework.success()


def test_method(FW):
    cases = []

    print("Resetting crownstone and waiting for dimmer to have started for a cleaner test.")
    sendCommandToCrownstone(ControlType.RESET, [])
    for t in reversed(range(7)):
        print("sleeping for {0} more seconds".format((t + 1) * 10))
        time.sleep(10)

    # print("set dimming allowed true.")
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1])
    time.sleep(0.5)

    # set override state to translucent so that twilight value should be used.
    sendCommandToCrownstone(ControlType.SWITCH, [0xfe])
    time.sleep(0.5)

    # clear the behaviour store via an internal event so that we know everything is
    # clean before starting the test.
    sendEventToCrownstone(0x100 + 170 + 6, [])
    time.sleep(5)

    result = []
    # for case in cases:
    #     result += [test_loopbody(FW, case)]
    return result


if __name__ == "__main__":
    with TestFramework(test_method) as frame:
        if frame != None:
            results = frame.test_run()
            prettyprinter = pprint.PrettyPrinter(indent=4)
            print ("Test finished with result:")
            for result in results:
                print(result)

        else:
            print(TestFramework.failure("Couldn't setup test framework"))
            print("remember, this test assumes behaviour store is clean before running")
