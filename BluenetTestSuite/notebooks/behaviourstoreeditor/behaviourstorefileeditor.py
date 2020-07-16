from ipywidgets import Button, Layout, Label, VBox, Text, Output

from behaviourstoreeditor.utils import *
from behaviourstoreeditor.icons import *

from behaviourstoreeditor.behaviourentryeditor import *
from behaviourstoreeditor.behaviourstoreserialisation import *

import json



class BehaviourStoreFileEditor:
    """
    Returns a widget and an update callback.
    """
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

    def get_widgets(self):
        return self.main_widget

    def update_content(self, filepath):
        if not filepath:
            # if empty, we clear the store editor, although we kep hold of the individual widgets
            self.behaviourstorefileeditor.children = []
            return
        else:
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
                    entry_editor_widgets = [BehaviourEntryEditor(BehaviourEntry(**entry), filepath) for entry in
                                            json_data['entries']]
                    self.behaviourstorefileeditorcontent.children = entry_editor_widgets
            except Exception as e:
                with file_editor_error_output_field:
                    print("failed reading json file")
                    print(e)

            # when first created, the children aren't displayed yet. that will happen on the first
            # call to this function, hence we set the children of the previously empty VBox.
            self.behaviourstorefileeditor.children = self.behaviourstorefileeditor_children

            ### footer
            # need to remove previous click handlers in order to not add stuff to files we opened in the past..
            self.addbehaviourbutton._click_handlers.callbacks = []
            self.addbehaviourbutton.on_click(lambda x: self.addbehaviourbutton_click(filepath))

    def addbehaviourbutton_click(self, filepath):
        """
        Callback that will write a new behaviour entry into the given path.
        No checking implemented yet.
        """
        with open(filepath, "r+") as json_file:
            json_data = json.load(json_file)
            new_behaviour_entry = BehaviourEntry()

            json_data["entries"] += [new_behaviour_entry.__dict__]
            json_file.seek(0)  # rewind
            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

            # append new widget

            self.behaviourstorefileeditorcontent.children += (
                BehaviourEntryEditor(new_behaviour_entry, filepath),
            )

