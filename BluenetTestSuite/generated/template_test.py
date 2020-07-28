"""
Generated with 'generatetestfromjson.py'.

TODO: add sys args, git context etc.
"""
import json

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *

from BluenetTestSuite.notebooks.behaviourstoreeditor.behaviourstoreserialisation import *

inputfolder = "/home/arend/Documents/bluenet-test-suite/bluenet-test-suite/BluenetTestSuite/json/"
outputfolder = "/home/arend/Documents/bluenet-test-suite/bluenet-test-suite/BluenetTestSuite/generated/"

behaviourstorefilename = "testbehaviourstoreA.behaviourstore.json"
scenariofilename = "testscenarioA.scenario.json"

def load_behaviourstore():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(5)

    with open(inputfolder + behaviourstorefilename,"r") as store_file:
        json_data = json.load(store_file)
        behaviourstore = BehaviourStore(**json_data)
        for behaviourentry in behaviourstore.entries:
            print(behaviourentry.guid, behaviourentry.index, behaviourentry.getBehaviour().getPacket())
            sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [behaviourentry.index] + behaviourentry.getBehaviour().getPacket())

def build_scenario(FW):
    """ /home/arend/Documents/bluenet-test-suite/bluenet-test-suite/BluenetTestSuite/json/testscenarioA.scenario.json """
    scenario = TestScenario(FW, F"{behaviourstorefilename}_{scenariofilename}")
    scenario.addEvent(load_behaviourstore)

    scenario.setGuid("00226e6cb9c3464c9f311a46c6775ac6")
    scenario.wait()
    
    scenario.setGuid("bbfee7ab8015464ab9d1443a59634722")
    scenario.setComment("should have clean init values")
    
    scenario.setGuid("85ac0174884a4f6b957c75db8ded4d31")
    scenario.setTime_secondssincemidnight(32400)
    scenario.addExpect("SwitchAggregator", "overrideState", "-1")
    
    scenario.setGuid("402e1bf8a8774fee9cd0f510e82d81dc")
    scenario.setComment("another comment here")
    
    scenario.setGuid("0eac1c7e9c2047d5aeb28c87dd2b0cf4")
    scenario.setTime_secondssincemidnight(34200)
    scenario.addExpectAny("SwitchAggregator", "behaviourState", ["0","-1"])
    
    return scenario

def run_test(FW):
    fullReset()
    setAllowDimming(True)

    time.sleep(5)

    scenario = build_scenario(FW)
    print("running scenario '{0}'".format(scenario.name))
    result = scenario.run()
    return result

if __name__ == "__main__":
    with TestFramework(run_test) as framework:
        if framework is not None:
            result = framework.test_run()
            prettyprinter = pprint.PrettyPrinter(indent=4)
            print ("Test finished with result:")
            print(result)
        else:
            print(TestFramework.failure("Couldn't setup test framework"))
            print("remember, this test assumes behaviour store is clean before running")

        
