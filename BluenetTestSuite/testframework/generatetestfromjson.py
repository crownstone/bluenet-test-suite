import sys, json

from BluenetTestSuite.notebooks.utils import *

inputfolder = "/home/arend/Documents/bluenet-test-suite/bluenet-test-suite/BluenetTestSuite/json/"
outputfolder = "/home/arend/Documents/bluenet-test-suite/bluenet-test-suite/BluenetTestSuite/generated/"

behaviourstorefilename = "testbehaviourstoreA" + BEHAVIOURSTORE_FILE_EXT
scenariofilename = "testscenarioA" + SCENARIO_FILE_EXT


def write_preamble(output):
    """
    Import files etc.
    """
    print(
        """\"\"\"
Generated with \'generatetestfromjson.py\'.

TODO: add sys args, git context etc.
\"\"\"

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *

""",
        file=output
    )

def write_behaviour_store_setup(output, storepath):
    """
    append setup code for the behaviour store to output
    """
    print(
        """
def load_behaviourstore():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(5)
""",
    file=output)

    with open(storepath,"r") as store:
        json_data = json.load(store)
        for behaviour in json_data['entries']:
            print(behaviour, file=output) # TODO: transform behaviour into actual behaviour packet


def write_postamble(output):
    print(
        """
        """,
        file=output
    )

if __name__=='__main__':
    with open(outputfolder + "firsttest.py","w") as outfile:
        write_preamble(outfile)
        write_behaviour_store_setup(outfile, inputfolder + behaviourstorefilename)
