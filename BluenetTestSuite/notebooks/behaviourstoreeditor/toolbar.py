from ipywidgets import ToggleButton, Layout,Button

from behaviourstoreeditor.icons import *
from behaviourstoreeditor.behaviourstoreserialisation import *

def ToolbarSummary(behaviour_entry, filepath):
    editbutton = ToggleButton(
        value=False,  # meaning 'collapsed'
        tooltip='Expand',
        disabled=False,
        icon=icon_edit,
        layout=Layout(width='100%')
    )

    return [editbutton]


def ToolbarDetails(behaviour_entry, filepath):
    deletebutton = Button(
        tooltip='Delete',
        disabled=False,
        icon=icon_delete,
        layout=Layout(width='100%')
    )

    savebutton = Button(
        tooltip='Save',
        disabled=False,
        icon=icon_save,
        layout=Layout(width='100%')
    )

    reloadbutton = Button(
        tooltip='Reload',
        disabled=False,
        icon=icon_reload,
        layout=Layout(width='100%')
    )

    return [savebutton, reloadbutton, deletebutton]
