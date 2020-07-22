from ipywidgets import ToggleButton, Layout, Button

from icons import *

class Toolbar:
    def __init__(self, scenario_event, filepath):
        self.editbutton = ToggleButton(
            value=False,  # meaning 'collapsed'
            tooltip='Expand',
            disabled=False,
            icon=icon_edit,
            layout=Layout(width='100%')
        )
        self.deletebutton = Button(
            tooltip='Delete',
            disabled=False,
            icon=icon_delete,
            layout=Layout(width='100%')
        )

        self.savebutton = Button(
            tooltip='Save',
            disabled=False,
            icon=icon_save,
            layout=Layout(width='100%')
        )
        self.reloadbutton = Button(
            tooltip='Reload',
            disabled=False,
            icon=icon_reload,
            layout=Layout(width='100%')
        )

        self.details = [self.savebutton, self.reloadbutton, self.deletebutton]
        self.summary = [self.editbutton]
