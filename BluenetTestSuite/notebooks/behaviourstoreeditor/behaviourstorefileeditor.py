from ipywidgets import Button, Layout, Label, VBox, Text, Output

from behaviourstoreeditor.utils import *
from behaviourstoreeditor.icons import *

from behaviourstoreeditor.behaviourentryeditor import *
from behaviourstoreeditor.behaviourstoreserialisation import *

import json

file_editor_error_output_field = Output()  # used for error reporting

addbehaviourbutton = reloadbutton = Button(
    tooltip='Add new behaviour to file',
    disabled=False,
    icon=icon_create,
    layout=Layout(width='100%')
)

behaviourstorefileeditorlegend = MakeHBox_single(
        [
            MakeHBox_single([Label("Index:")], ['100%']),
            MakeHBox_single([Label(F"{i:02d}:00") for i in range(0, 24, 6)], ['25%' for i in range(4)])
        ],
        ['5%', '90%']
    )

behaviourstorefileeditorheader = VBox([
    behaviourstorefileeditorlegend
])

behaviourstorefileeditorfooter = MakeHBox_single([addbehaviourbutton], ['5%'])

# behaviourstorefileeditorcontent = MakeHBox_single([Label("content not initialized", layout=Layout(width='100%'))], ['100%'])
behaviourstorefileeditorcontent = VBox([Label("content not initialized", layout=Layout(width='100%'))])

behaviourstorefileeditor_children = [
        behaviourstorefileeditorheader,
        behaviourstorefileeditorcontent,
        behaviourstorefileeditorfooter,
        file_editor_error_output_field
    ]

behaviourstorefileeditor = VBox(children=[], layout=Layout(width='100%'))

def createOnAddBehaviourButtonCallback(filepath):
    """
    returns a 1-parameter callback button that will write a new behaviour entry into the given path.
    No checking implemented yet.
    """
    def onAdd(b):
        with open(filepath,"r+") as json_file:
            json_data = json.load(json_file)
            json_data["entries"] += [json.dumps(BehaviourEntry().__dict__)]
            json_file.seek(0)  # rewind
            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

            # append new widget
            behaviourstorefileeditorcontent.children += (BehaviourEntryEditor(), )

    return onAdd

def BehaviourStoreUpdateContent(filepath):
    if not filepath:
        # if empty, we clear the store editor.
        behaviourstorefileeditor.children = []
        return
    else:
        ### header
        behaviourstorefileeditorheader.children = [
            MakeHBox_single([Label("Current file:", layout=Layout(width='100%')),
                             Text(F"{filepath}", layout=Layout(width='100%'), disabled=True)],
                            ['10', '90%']),
            behaviourstorefileeditorlegend
        ]

        ### content
        try:
            with open(filepath, "r") as json_file:
                json_data = json.load(json_file)
                entry_editor_widgets = [BehaviourEntryEditor() for entry in json_data['entries']]
                behaviourstorefileeditorcontent.children = entry_editor_widgets
        except Exception as e:
            with file_editor_error_output_field:
                print("failed reading json file")
                print(e)

        # when first created, the children aren't displayed yet. that will happen on the first
        # call to this function, hence we set the children of the previously empty VBox.
        behaviourstorefileeditor.children = behaviourstorefileeditor_children

        ### footer

        # need to remove previous click handlers in order to not add stuff to files we opened in the past..
        addbehaviourbutton._click_handlers.callbacks = []
        addbehaviourbutton.on_click(createOnAddBehaviourButtonCallback(filepath))

def BehaviourStoreFileEditor():
    """
    Returns a widget and an update callback.
    """
    return behaviourstorefileeditor, BehaviourStoreUpdateContent
