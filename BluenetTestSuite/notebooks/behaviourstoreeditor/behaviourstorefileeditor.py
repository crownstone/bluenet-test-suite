from ipywidgets import Button, Layout, Label, VBox, Text

from behaviourstoreeditor.utils import *
from behaviourstoreeditor.icons import *

from behaviourstoreeditor.behaviourstoreserialisation import *

import json

addbehaviourbutton = reloadbutton = Button(
    tooltip='Add new behaviour to file',
    disabled=False,
    icon=icon_create,
    layout=Layout(width='100%')
)

behaviourstorefileeditorheader = MakeHBox_single(
        [
            MakeHBox_single([Label("Index:")], ['100%']),
            MakeHBox_single([Label(F"{i:02d}:00") for i in range(0, 24, 6)], ['25%' for i in range(4)])
        ],
        ['5%', '90%']
    )

behaviourstorefileeditorfooter = MakeHBox_single([addbehaviourbutton], ['5%'])

behaviourstorefileeditorcontent = MakeHBox_single([Label("content not initialized")], ['100%'])

behaviourstorefileeditor_children = [
        behaviourstorefileeditorheader,
        behaviourstorefileeditorcontent,
        behaviourstorefileeditorfooter
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

    return onAdd

def BehaviourStoreUpdateContent(filepath):
    if not filepath:
        # if empty, we clear the store editor.
        behaviourstorefileeditor.children = []
        return
    else:
        # with open... read json extract children.
        behaviourstorefileeditorcontent.children = [Text(F"loaded: '{filepath}'", layout=Layout(width='100%'))]

        # when first created, the children aren't displayed yet. that will happen on the first
        # call to this function, hence we set the children of the previously empty VBox.
        behaviourstorefileeditor.children = behaviourstorefileeditor_children

        # need to remove previous click handlers in order to not add stuff to files we opened in the past..
        addbehaviourbutton._click_handlers.callbacks = []
        addbehaviourbutton.on_click(createOnAddBehaviourButtonCallback(filepath))

def BehaviourStoreFileEditor():
    """
    Returns a widget and an update callback.
    """
    return behaviourstorefileeditor, BehaviourStoreUpdateContent
