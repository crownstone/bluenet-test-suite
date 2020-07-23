from ipywidgets import VBox, Button, Output

from utils import *
from icons import *
from scenarioeditor.scenarioserialisation import *

from scenarioeditor.metadata import *
from scenarioeditor.eventcontent import *
from scenarioeditor.toolbar import *

import json


class ScenarioEventEditor:
    def __init__(self, scenario_event, filepath):
        self.filepath = filepath
        self.scenario_event = scenario_event

        # widget subgroups
        self.output = Output()

        self.metadata = MetaData(scenario_event, filepath)
        self.eventcontent = EventContent(scenario_event, filepath)
        self.toolbar = Toolbar(scenario_event, filepath)

        # top level widget group
        self.summary = MakeHBox([self.metadata.summary, self.eventcontent.summary, self.toolbar.summary], ['5%', '90%', '5%'])
        self.details = VBox(children=[
            MakeHBox([self.metadata.details, self.eventcontent.details, self.toolbar.details], ['5%', '90%', '5%']),
            self.output
        ])

        self.event_editor = VBox([self.summary], layout=Layout(width='100%'))

        # concrete widget forwards
        self.deletebutton = self.toolbar.deletebutton

        # populate metadata with initial content
        self.metadata.set(self.eventcontent.get())

        self.setup_interaction()

    def get_widgets(self):
        return self.event_editor

    def setup_interaction(self):
        self.eventcontent.timeslider.observe(lambda x: self.metadata.set(self.eventcontent.get()), 'value')
        self.eventcontent.timepicker.observe(lambda x: self.metadata.set(self.eventcontent.get()), 'value')

        self.toolbar.editbutton.observe(lambda x: self.toggle_detail_widgets(x), 'value')
        self.toolbar.savebutton.on_click(lambda x: self.save(x))
        self.toolbar.reloadbutton.on_click(lambda x: self.reload(x))
        self.toolbar.deletebutton.on_click(lambda x: self.delete(x))

    def toggle_detail_widgets(self, observation):
        if self.toolbar.editbutton.value:
            self.event_editor.children = [self.summary, self.details]
            self.toolbar.editbutton.tooltip = "Collapse"
            self.toolbar.editbutton.icon = icon_minimize
        else:
            self.event_editor.children = [self.summary]
            self.toolbar.editbutton.tooltip = "Expand"
            self.toolbar.editbutton.icon = icon_edit

    def reload(self, b):
        with open(self.filepath, "r+") as json_file:
            scene = ScenarioDescription(**json.load(json_file))

            try:
                event = next(event for event in scene.events if event.guid == self.scenario_event.guid)
                self.eventcontent.set(event)
            except StopIteration as e:
                pass

    def delete(self, b):
        with open(self.filepath, "r+") as json_file:
            scene = ScenarioDescription(**json.load(json_file))
            scene.events = [event for event in scene.events if event.guid != self.scenario_event.guid]

            json_file.seek(0)  # rewind
            json.dump(scene, json_file, indent=4, default=lambda x: x.__dict__)
            json_file.truncate()

    def save(self, b):
        with open(self.filepath, "r+") as json_file:
            scene = ScenarioDescription(**json.load(json_file))
            scene.events = [(event if event.guid != self.scenario_event.guid else self.eventcontent.get()) for event in scene.events]

            json_file.seek(0)  # rewind
            json.dump(scene, json_file, indent=4, default=lambda x: x.__dict__)
            json_file.truncate()

    def get_event(self):
        return self.eventcontent.get()