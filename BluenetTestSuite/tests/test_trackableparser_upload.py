"""
Uploads a single CuckooFilter to the firmware by injecting an event on the bus.

TODO: Expand to test functionality beyond this command.
"""
from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *

def sendUploadCommandOverFirmwareBus(uploadpacket):
    uint8_t filterId;
    uint16_t chunkStartIndex;
    uint16_t totalSize;
    uint16_t chunkSize;
    uint8_t chunk[];
    sendEventToCrownstone(0x100 + 190 + 9, uploadpacket)



def buildScenarioUploadFilterAsSingleChunk(FW):
    """
    Uploads a filter as single chunk.
    """
    scenario = TestScenario(FW, "UploadFilterAsSingleChunk")

    # a 0-ary lambda returning None should be considered success.
    # TODO: Expand to actual functionality.
    scenario.addEvent(lambda: None)

def run_all_scenarios(FW):
    fullReset()

    result = []

    scenarios = [
        buildScenarioUploadFilterAsSingleChunk(FW),
    ]

    for scenario in scenarios:
        print("running scenario '{0}'".format(scenario.name))
        result += [scenario.run()]

    return result


if __name__ == "__main__":
    with TestFramework(run_all_scenarios) as framework:
        if framework is not None:
            results = framework.test_run()
            prettyprinter = pprint.PrettyPrinter(indent=4)
            print ("Test finished with result:")
            for result in results:
                print(result)
        else:
            print(TestFramework.failure("Couldn't setup test framework"))
