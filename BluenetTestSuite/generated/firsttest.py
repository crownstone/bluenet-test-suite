"""
Generated with 'generatetestfromjson.py'.

TODO: add sys args, git context etc.
"""

from BluenetTestSuite.testframework.framework import *
from BluenetTestSuite.testframework.scenario import *
from BluenetTestSuite.firmwarecontrol.switchaggregator import *
from BluenetTestSuite.firmwarecontrol.behaviourstore import *



def load_behaviourstore():
    sendSwitchAggregatorReset()
    sendClearBehaviourStoreEvent()
    time.sleep(5)

{'guid': 'c137e4a5078b4e0abc8e94d5f40c68a7', 'index': 0, 'fromfield': 32400, 'untilfield': 64800, 'intensityfield': 80, 'fromuntil_reversed_field': False, 'typefield': 'Switch'}
{'guid': 'd1187b1aaa114d0c90a068fd263107de', 'index': 1, 'fromfield': 0, 'untilfield': 64800, 'intensityfield': 80, 'fromuntil_reversed_field': False, 'typefield': 'Switch'}
