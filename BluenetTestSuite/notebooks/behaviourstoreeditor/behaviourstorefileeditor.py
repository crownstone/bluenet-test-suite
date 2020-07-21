from ipywidgets import Button, Layout, Label, VBox, Text, Output

from utils import *
from icons import *

from behaviourstoreeditor.behaviourentryeditor import *
from behaviourstoreeditor.behaviourstoreserialisation import *

import json



class BehaviourStoreFileEditor:
    def __init__(self):
        self.file_editor_error_output_field = Output()  # used for error reporting

        self.addbehaviourbutton = Button(
            tooltip='Add new behaviour to file',
            disabled=False,
            icon=icon_create,
            layout=Layout(width='100%')
        )

        self.behaviourstorefileeditorlegend = MakeHBox_single(
            [
                MakeHBox_single([Label("Index:")], ['100%']),
                MakeHBox_single([Label(F"{i:02d}:00") for i in range(0, 24, 6)], ['25%' for i in range(4)])
            ],
            ['5%', '90%']
        )

        self.behaviourstorefileeditorheader = VBox([
            self.behaviourstorefileeditorlegend
        ])

        self.behaviourstorefileeditorfooter = MakeHBox_single([self.addbehaviourbutton], ['5%'])

        self.behaviourstorefileeditorcontent = VBox([Label("content not initialized", layout=Layout(width='100%'))])

        self.behaviourstorefileeditor_children = [
            self.behaviourstorefileeditorheader,
            self.behaviourstorefileeditorcontent,
            self.behaviourstorefileeditorfooter,
            self.file_editor_error_output_field
        ]

        self.behaviourstorefileeditor = VBox(children=[], layout=Layout(width='100%'))

        self.main_widget = MakeHBox_single([self.behaviourstorefileeditor], ['100%'])

        # run time variables
        self.entryeditors = []
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
        ### header
        self.behaviourstorefileeditorheader.children = [
            MakeHBox_single([Label("Current file:", layout=Layout(width='100%')),
                             Text(F"{filepath}", layout=Layout(width='100%'), disabled=True)],
                            ['10', '90%']),
            self.behaviourstorefileeditorlegend
        ]

        ### content
        try:
            with open(filepath, "r") as json_file:
                json_data = json.load(json_file)
                self.entryeditors = [BehaviourEntryEditor(BehaviourEntry(**entry), filepath) for entry in
                                        json_data['entries']]
                self.update_editor_content_widgets()
        except Exception as e:
            with self.file_editor_error_output_field:
                print("failed reading json file")
                print(e)

        for entryeditor in self.entryeditors:
                entryeditor.deletebutton.on_click(lambda x: self.update_content(filepath))

        # when first created, the children aren't displayed yet. that will happen on the first
        # call to this function, hence we set the children of the previously empty VBox.
        self.behaviourstorefileeditor.children = self.behaviourstorefileeditor_children

        ### footer
        # need to remove previous click handlers in order to not add stuff to files we opened in the past..
        self.addbehaviourbutton._click_handlers.callbacks = []
        self.addbehaviourbutton.on_click(lambda x: self.addbehaviour(filepath))

        ### update file path.
        self.current_filepath = filepath

    def update_file_editor(self, filepath):
        """
        change as little as possible: only reload widgets that have changed and delete widgets that have disappeared
        """
        with self.file_editor_error_output_field:
            print("updating file editor")

        # todo: this is quite brutal and collapses all the entry editors...
        self.create_file_editor(filepath)
        # try:
        #     with open(filepath, "r") as json_file:
        #         json_data = json.load(json_file)
        # except Exception as e:
        #     with self.file_editor_error_output_field:
        #         print("failed updating")

    def save_all(self, filepath):
        """
        Saves all changes to the file at location 'filepath'
        """
        if not filepath:
            return
        with self.file_editor_error_output_field:
            print(F"saving all entry changes to {filepath}")
        with open(filepath, "w") as json_file:
            store = BehaviourStore()
            store.entries = [(entry_editor.get_behaviour_entry()) for entry_editor in self.entryeditors]
            json.dump(store, json_file, indent=4, default=lambda x: x.__dict__)

    def update_editor_content_widgets(self):
        self.behaviourstorefileeditorcontent.children = [entryeditor.get_widgets() for entryeditor in self.entryeditors]

    def addbehaviour(self, filepath):
        """
        Callback that will write a new behaviour entry into the given path.
        No checking implemented yet.
        """
        with open(filepath, "r+") as json_file:
            json_data = json.load(json_file)
            new_behaviour_entry = BehaviourEntry()

            # get available index
            indices = sorted([editor.get_behaviour_entry().index for editor in self.entryeditors])
            while new_behaviour_entry.index in indices:
                new_behaviour_entry.index += 1

            json_data["entries"] += [new_behaviour_entry.__dict__]
            json_file.seek(0)  # rewind
            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

            # append new widget
            self.entryeditors += [BehaviourEntryEditor(new_behaviour_entry, filepath)]
            self.behaviourstorefileeditorcontent.children += (
                self.entryeditors[-1].get_widgets(),
            )

