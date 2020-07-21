from ipywidgets import VBox, Button

from utils import *
from icons import *
from scenarioeditor.scenarioserialisation import *

class ScenarioEventEditor:
    def __init__(self, scenario_event, filepath):
        self.filepath = filepath
        self.scenario_event = scenario_event
        self.event_editor = VBox()

        self.deletebutton = Button()

    def get_widgets(self):
        return self.event_editor