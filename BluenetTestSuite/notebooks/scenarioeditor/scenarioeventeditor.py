from ipywidgets import VBox, Button, Output

from utils import *
from icons import *
from scenarioeditor.scenarioserialisation import *

from scenarioeditor.metadata import *
from scenarioeditor.eventcontent import *
from scenarioeditor.toolbar import *
from scenarioeditor.scenariodebugview import *

import json


class ScenarioEventEditor:
    def __init__(self, scenario_event, filepath):
        self.filepath = filepath
        self.scenario_event = scenario_event

        # view options
        self.unfolded = False
        self.debugmode = False

        # widget subgroups
        self.metadata = MetaData(scenario_event, filepath)
        self.eventcontent = EventContent(scenario_event, filepath)
        self.toolbar = Toolbar(scenario_event, filepath)
        self.debugview = ScenarioDebugView(scenario_event, filepath)

        # top level widget group
        self.summary = self.get_summary()
        self.details = self.get_details()
        self.debugviewwidgets = self.debugview.get_widgets()

        self.event_editor = VBox([self.summary], layout=Layout(width='100%'))

        # concrete widget forwards
        self.deletebutton = self.toolbar.deletebutton

        # populate metadata with initial content
        self.metadata.set(self.eventcontent.get())
        self.reload_view()
        self.setup_interaction()

    def get_widgets(self):
        """
        returns the top level widget, which can be embedded in other contained widgets.
        """
        return self.event_editor

    def get_summary(self):
        return MakeHBox([self.metadata.summary, self.eventcontent.summary, self.toolbar.summary], ['5%', '90%', '5%'])

    def get_details(self):
        return VBox(children=[
            MakeHBox([self.metadata.details, self.eventcontent.details, self.toolbar.details], ['5%', '90%', '5%'])
        ])

    def set_debug_view(self, active):
        self.debugmode = active
        self.reload_view()

    def setup_interaction(self):
        self.eventcontent.timeslider.observe(lambda x: self.metadata.set(self.eventcontent.get()), 'value')
        self.eventcontent.timepicker.observe(lambda x: self.metadata.set(self.eventcontent.get()), 'value')

        self.toolbar.editbutton.observe(lambda x: self.toggle_detail_widgets(x), 'value')
        self.toolbar.savebutton.on_click(lambda x: self.save(x))
        self.toolbar.reloadbutton.on_click(lambda x: self.reload(x))
        self.toolbar.deletebutton.on_click(lambda x: self.delete(x))

    def toggle_detail_widgets(self, observation):
        if self.toolbar.editbutton.value:
            self.unfolded = True
            self.toolbar.editbutton.tooltip = "Collapse"
            self.toolbar.editbutton.icon = icon_minimize
        else:
            self.unfolded = False
            self.toolbar.editbutton.tooltip = "Expand"
            self.toolbar.editbutton.icon = icon_edit
        self.reload_view()

    def reload_view(self):
        """
        Updates event_editor.children to match the current view settings.
        """
        viewlist = [self.summary]
        viewlist += [self.details] if self.unfolded else []
        viewlist += [self.debugviewwidgets] if self.debugmode else []
        self.event_editor.children = viewlist

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