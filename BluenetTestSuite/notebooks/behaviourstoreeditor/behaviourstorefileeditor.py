from ipywidgets import Button, Layout, Label, VBox

from behaviourstoreeditor.utils import *

from behaviourstoreeditor.icons import *

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

behaviourstorefileeditorcontent = VBox([Button(description=F"hi")])

behaviourstorefileeditor = VBox([
        behaviourstorefileeditorheader,
        behaviourstorefileeditorcontent,
        behaviourstorefileeditorfooter
    ])


def BehaviourStoreUpdateContent(filepath):
    # with open... read json extract children.
    behaviourstorefileeditorcontent.children = [Button(description=F"hi '{filepath}'")]

def BehaviourStoreFileEditor():
    """
    Returns a widget and an update callback.
    """
    return behaviourstorefileeditor, BehaviourStoreUpdateContent
