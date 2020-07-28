import sys, json

from BluenetTestSuite.notebooks.utils import *
from BluenetTestSuite.notebooks.behaviourstoreeditor.behaviourstoreserialisation import *
from BluenetTestSuite.notebooks.scenarioeditor.scenarioserialisation import *

inputfolder = "/home/arend/Documents/bluenet-test-suite/bluenet-test-suite/BluenetTestSuite/json/"
outputfolder = "/home/arend/Documents/bluenet-test-suite/bluenet-test-suite/BluenetTestSuite/generated/"

behaviourstorefilename = "testbehaviourstoreA" + BEHAVIOURSTORE_FILE_EXT
scenariofilename = "testscenarioA" + SCENARIO_FILE_EXT

def write_preamble(output):
    """
    Import files etc.
    """
    print(
        F"""\"\"\"
Generated with \'generatetestfromjson.py\'.

TODO: add sys args, git context etc.
\"\"\"
import json

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *

from BluenetTestSuite.notebooks.behaviourstoreeditor.behaviourstoreserialisation import *

inputfolder = \"{inputfolder}\"
outputfolder = \"{outputfolder}\"

behaviourstorefilename = \"{behaviourstorefilename}\"
scenariofilename = \"{scenariofilename}\"
""",
        file=output
    )

def write_behaviour_store_setup(output):
    """
    append setup code for the behaviour store to output
    """
    print(
    F"""def load_behaviourstore():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(5)

    with open(inputfolder + behaviourstorefilename,"r") as store_file:
        json_data = json.load(store_file)
        behaviourstore = BehaviourStore(**json_data)
        for behaviourentry in behaviourstore.entries:
            print(behaviourentry.guid, behaviourentry.index, behaviourentry.getBehaviour().getPacket())
            sendCommandToCrownstone(ControlType.REPLACE_BEHAVIOUR, [behaviourentry.index] + behaviourentry.getBehaviour().getPacket())
""",
        file=output
    )

def write_scenario_setup(output):
    print(
        F"""def build_scenario(FW):
    \"\"\" {inputfolder + scenariofilename} \"\"\"""", file=output)
    print("""    scenario = TestScenario(FW, F"{behaviourstorefilename}_{scenariofilename}")
    scenario.addEvent(load_behaviourstore)
""", file=output
    )

    with open(inputfolder + scenariofilename, "r") as scene_file:
        scene = ScenarioDescription(**json.load(scene_file))
        for event in scene.events:
            # print(F"    # {event.guid}", file=output)
            print(F"    scenario.setGuid(\"{event.guid}\")", file=output)
            if event.time is not None:
                print(F"    scenario.setTime_secondssincemidnight({event.time})", file=output)
            print(F"    scenario.{event.commandname}({event.arguments})", file=output)
            print("    ",file=output)

    print("    return scenario", file=output)
    print("", file=output)

def write_postamble(output):
    print(
        """def run_test(FW):
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

        """,
        file=output
    )

if __name__=='__main__':
    with open(outputfolder + "template_test.py","w") as outfile:
        write_preamble(outfile)
        write_behaviour_store_setup(outfile)
        write_scenario_setup(outfile)
        write_postamble(outfile)
