import time

from testframework.framework import *
from firmwarecontrol.datatransport import *
from BluenetLib.lib.protocol.BluenetTypes import ControlType
from BluenetLib.lib.packets.behaviour.Behaviour import *


def buildTwilight(from_hours, to_hours, intensity):
    twilight = Twilight()
    twilight.setTimeFrom(from_hours % 24, 0)
    twilight.setTimeTo(to_hours % 24, 0)
    twilight.setDimPercentage(intensity)
    return twilight


def sendTwilight(index, twilight):
    packet = twilight.getPacket()
    sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [index] + twilight.getPacket())


class test_case:
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

    def timelist(self):
        return sorted([self.t0.fromTime.offset, self.t1.fromTime.offset,
                       self.t0.untilTime.offset, self.t1.untilTime.offset])

    def ex_time(self, index):
        tl = self.timelist()
        return int((tl[index] + tl[index + 1]) / 2.0)

    def print(self):
        print("case {7}: t0=[{0},{1}] t1=[{2},{3}], expect [{4},{5},{6}]".format(
            self.t0.fromTime.offset // 3600, self.t0.untilTime.offset // 3600,
            self.t1.fromTime.offset // 3600, self.t1.untilTime.offset // 3600,
            self.e[0], self.e[1], self.e[2], self.id
        ))


def test_twilightconflictresolution_loopbody(FW, testcase):
    """
    Test will assume a clean behaviour store, except for possibly index 0 and 1,
    which will be overwritten by the current test case twilights.
    It also assumes that dimming is allowed and the dimmer has started.
    """
    print("##### setup test_twilightconflictresolution_loopbody #####")
    testcase.print()

    # send twilights to behaviour store
    sendTwilight(0, testcase.t0)
    time.sleep(0.2)
    sendTwilight(1, testcase.t1)

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
        time.sleep(1)

        failures = FW.assertFindFailures("TwilightHandler", 'previousIntendedState', testcase.e[i])
        if failures:
            failmsg = TestFramework.failure("failed case {0},{1} at time: {2}. Expected {3}".format(
                testcase.id, i, testtime, testcase.e[i]))
            testcase.print()
            FW.print()
            return failmsg

    return TestFramework.success()


def test_twilightconflictresolution(FW):
    cases = []
    # span of testcases: 0--3 for partially and fully overlapping, 0--2 same start time, 0--2 same start/end.
    for hr_offset in [0, 12, 21, 22, 23]:
        cases += test_case(buildTwilight(0 + hr_offset, 2 + hr_offset, 50),
                           buildTwilight(1 + hr_offset, 3 + hr_offset, 75), [50, 75, 75]),  # partially overlapping
        cases += test_case(buildTwilight(0 + hr_offset, 2 + hr_offset, 75),
                           buildTwilight(1 + hr_offset, 3 + hr_offset, 50), [50, 50, 75]),  # partially overlapping
        cases += test_case(buildTwilight(0 + hr_offset, 3 + hr_offset, 50),
                           buildTwilight(1 + hr_offset, 2 + hr_offset, 75), [50, 75, 50]),  # full overlap, increasing
        cases += test_case(buildTwilight(0 + hr_offset, 3 + hr_offset, 75),
                           buildTwilight(1 + hr_offset, 2 + hr_offset, 50), [75, 50, 75]),  # full overlap, decreasing
        cases += test_case(buildTwilight(0 + hr_offset, 2 + hr_offset, 50),
                           buildTwilight(0 + hr_offset, 1 + hr_offset, 75), [75, 75, 50]),  # same starttime, increasing
        cases += test_case(buildTwilight(0 + hr_offset, 2 + hr_offset, 75),
                           buildTwilight(0 + hr_offset, 1 + hr_offset, 50), [50, 50, 75]),  # same starttime, decreasing
        cases += test_case(buildTwilight(0 + hr_offset, 2 + hr_offset, 75),
                           buildTwilight(0 + hr_offset, 2 + hr_offset, 50), [50, 50, 0]),  # same starttime and endtime
                                                                                           # last case ex_time[2] will
                                                                                           # falls at 02:00+offset.

    print("Resetting crownstone and waiting for dimmer to have started for a cleaner test.")
    sendCommandToCrownstone(ControlType.RESET, [])
    for t in reversed(range(7)):
        print("sleeping for {0} more seconds".format((t + 1) * 10))
        time.sleep(10)

    # print("set dimming allowed true.")
    sendCommandToCrownstone(ControlType.ALLOW_DIMMING, [1])
    time.sleep(0.5)

    # set override state to translucent so that twilight value should be used.
    sendCommandToCrownstone(ControlType.SWITCH, [0xff])
    time.sleep(0.5)

    result = []
    for case in cases:
        result += [test_twilightconflictresolution_loopbody(FW, case)]
    return result


if __name__ == "__main__":
    with TestFramework(test_twilightconflictresolution) as frame:
        if frame != None:
            result = frame.test_run()
            prettyprinter = pprint.PrettyPrinter(indent=4)
            prettyprinter.pprint(result)

        else:
            print(TestFramework.failure("Couldn't setup test framework"))
            print("remember, this test assumes behaviour store is clean before running")
