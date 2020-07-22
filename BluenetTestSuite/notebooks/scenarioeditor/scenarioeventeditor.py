from ipywidgets import VBox, Button

from utils import *
from icons import *
from scenarioeditor.scenarioserialisation import *

from scenarioeditor.toolbar import *
from scenarioeditor.metadata import *

class ScenarioEventEditor:
    def __init__(self, scenario_event, filepath):
        self.filepath = filepath
        self.scenario_event = scenario_event

        # widget subgroups
        self.toolbar = Toolbar(scenario_event, filepath)
        self.metadata = MetaData(scenario_event, filepath)

        self.event_summary = []#VBox()
        self.event_details = []#VBox()

        # top level widget group
        self.summary = MakeHBox([self.metadata.summary, self.event_summary, self.toolbar.summary], ['5%', '90%', '5%'])
        self.details = MakeHBox([self.metadata.details, self.event_details, self.toolbar.details], ['5%', '90%', '5%'])

        self.event_editor = VBox([self.summary], layout=Layout(width='100%'))

        # concrete widget forwards
        self.deletebutton = self.toolbar.deletebutton

        self.setup_interaction()

    def get_widgets(self):
        return self.event_editor

    def setup_interaction(self):
        # register 'on edit button click'
        self.toolbar.editbutton.observe(lambda x: self.toggle_detail_widgets(x), 'value')

    def toggle_detail_widgets(self, observation):
        if self.toolbar.editbutton.value:
            self.event_editor.children = [self.summary, self.details]
            self.toolbar.editbutton.tooltip = "Collapse"
            self.toolbar.editbutton.icon = icon_minimize
        else:
            self.event_editor.children = [self.summary]
            self.toolbar.editbutton.tooltip = "Expand"
            self.toolbar.editbutton.icon = icon_edit

