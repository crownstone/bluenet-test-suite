from ipywidgets import Button, Layout, Label, VBox

from behaviourstoreeditor.utils import *

from behaviourstoreeditor.icons import *

addbehaviourbutton = reloadbutton = Button(
    tooltip='Add new behaviour to file',
    disabled=False,
    icon=icon_create,
    layout=Layout(width='100%')
)


def BehaviourStoreFileEditorHeader():
    return MakeHBox_single(
        [
            MakeHBox_single([Label("Index:")],['100%']),
            MakeHBox_single([Label(F"{i:02d}:00") for i in range(0, 24, 6)], ['25%' for i in range(4)])
        ],
        ['5%', '90%']
    )

def BehaviourStoreFileEditorFooter():
    return MakeHBox_single([addbehaviourbutton], ['5%'])

def BehaviourStoreFileEditorContent():
    return VBox()