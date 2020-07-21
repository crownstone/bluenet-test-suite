from ipywidgets import Button, Layout, Label, VBox, Text, Output

from icons import *
from utils import *

from scenarioeditor.scenarioeventeditor import *

import json

class ScenarioFileEditor:
    def __init__(self):
        self.file_editor_error_output_field = Output()  # used for error reporting

        self.addbehaviourbutton = Button(
            tooltip='Add new event to file',
            disabled=False,
            icon=icon_create,
            layout=Layout(width='100%')
        )

        self.behaviourstorefileeditorlegend = MakeHBox_single(
            [
                MakeHBox_single([Label("Time")], ['100%']),
                MakeHBox_single([Label(F"{i:02d}:00") for i in range(0, 24, 6)], ['25%' for i in range(4)])
            ],
            ['5%', '90%']
        )

        self.behaviourstorefileeditorheader = VBox([
            self.behaviourstorefileeditorlegend
        ])

        self.behaviourstorefileeditorfooter = MakeHBox_single([self.addbehaviourbutton], ['5%'])

        self.scenariofileeditorcontent = VBox([Label("content not initialized", layout=Layout(width='100%'))])

        self.behaviourstorefileeditor_children = [
            self.behaviourstorefileeditorheader,
            self.scenariofileeditorcontent,
            self.behaviourstorefileeditorfooter,
            self.file_editor_error_output_field
        ]

        self.behaviourstorefileeditor = VBox(children=[], layout=Layout(width='100%'))

        self.main_widget = MakeHBox_single([self.behaviourstorefileeditor], ['100%'])

        # run time variables
        self.eventeditors = []
        self.current_filepath = None

    def get_widgets(self):
        return self.main_widget

    def update_content(self, filepath):
        """
               construct, update or clear the fileeditor based on wether filepath is different from the current, identical, or None.
               """
        if not filepath:
            # if empty, we clear the store editor, although we kep hold of the individual widgets
            self.behaviourstorefileeditor.children = []
            self.current_filepath = None
            return
        elif filepath == self.current_filepath:
            self.update_file_editor(filepath)
        else:
            self.create_file_editor(filepath)

    def create_file_editor(self, filepath):
        """
        Reads filepath as json and constructs editor widget groups for each entry.
        Also constructs the header and footer for the behaviourstorefileeditor.
        """
        with self.file_editor_error_output_field:
            print(F"create editor for file: {filepath}")

        ###  adjust header information
        self.behaviourstorefileeditorheader.children = [
            MakeHBox_single([Label("Current file:", layout=Layout(width='100%')),
                             Text(F"{filepath}", layout=Layout(width='100%'), disabled=True)],
                            ['10', '90%']),
            self.behaviourstorefileeditorlegend
        ]

        ### read what content to load editors for
        try:
            with open(filepath, "r") as json_file:
                json_data = json.load(json_file)
                self.eventeditors = [ScenarioEventEditor(ScenarioEvent(**entry), filepath) for entry in
                                     json_data['events']]
                self.update_editor_content_widgets()
        except Exception as e:
            with self.file_editor_error_output_field:
                print("failed reading json file")
                print(e)

        # when first created, the children aren't displayed yet. that will happen on the first
        # call to this function, hence we set the children of the previously empty VBox.
        self.behaviourstorefileeditor.children = self.behaviourstorefileeditor_children

        self.current_filepath = filepath
        self.setup_interaction(filepath)

    def setup_interaction(self, filepath):
        for eventeditor in self.eventeditors:
            eventeditor.deletebutton.on_click(lambda x: self.update_content(filepath))

        # need to remove previous click handlers in order to not add stuff to files we opened in the past..
        self.addbehaviourbutton._click_handlers.callbacks = []
        self.addbehaviourbutton.on_click(lambda x: self.addevent(filepath))


    def update_file_editor(self, filepath):
        with self.file_editor_error_output_field:
            print(F"update editor for file: {filepath}")
        # todo: update this to a more friendly update rather than recreating the whole thing
        self.create_file_editor(filepath)

    def update_editor_content_widgets(self):
        self.scenariofileeditorcontent.children = [eventeditor.get_widgets() for eventeditor in self.eventeditors]

    def addevent(self, filepath):
        """
        Callback that will write a new behaviour entry into the given path.
        No checking implemented yet.
        """
        with self.file_editor_error_output_field:
            print("add event to list")

        with open(filepath, "r+") as json_file:
            json_data = json.load(json_file)
            new_scenario_event = ScenarioEvent()

            json_data["events"] += [new_scenario_event.__dict__]
            json_file.seek(0)  # rewind
            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

            # append new widget
            self.eventeditors += [ScenarioEventEditor(new_scenario_event, filepath)]
            self.scenariofileeditorcontent.children += (
                self.eventeditors[-1].get_widgets(),
            )

    def save_all(self, filepath):
        with self.file_editor_error_output_field:
            print("save all clicked")
