from ipywidgets import VBox

from behaviourstoreeditor.utils import *
from behaviourstoreeditor.icons import *
from behaviourstoreeditor.behaviourstoreserialisation import *

from behaviourstoreeditor.behaviourentry import *
from behaviourstoreeditor.entrymetadata import *
from behaviourstoreeditor.toolbar import *

import json

class BehaviourEntryEditor:
    """
    A collection of widgets used for editing BehaviourEntry-s. Concerns exactly one behaviour entry,
    identified by its file path and guid.
    """

    def __init__(self, behaviour_entry, filepath):
        """
        behaviour_entry is a BehaviourEntry, coming from the file at filepath.
        """
        self.filepath = filepath
        self.behaviour_entry = behaviour_entry

        # todo: callbacks can be called as normal methods once the relevant objects have been defined as actual classes
        self.summary_meta, \
            self.get_entry_metadata = MetaDataSummary(behaviour_entry, filepath)
        self.summary_overview, \
            self.overview_update_callback = BehaviourOverviewSummary(behaviour_entry, filepath)
        self.summary_toolbar = ToolbarSummary(behaviour_entry, filepath)

        self.details_meta = MetaDataDetails(behaviour_entry, filepath)
        self.details_overview, \
            self.get_behaviour_entry_details, \
            self.set_behaviour_entry_details = BehaviourOverviewDetails(behaviour_entry, filepath)
        self.details_toolbar = ToolbarDetails(behaviour_entry, filepath)

        self.summary = MakeHBox([summary_meta, summary_overview, summary_toolbar], ['5%', '90%', '5%'])
        self.details = MakeHBox([details_meta, details_overview, details_toolbar], ['5%', '90%', '5%'])

        self.entry_editor = VBox([summary], layout=Layout(width='100%'))

        # todo: remove these local variables once the toolbar is a class object with nice names.
        self.editbutton = summary_toolbar[0]
        self.savebutton = details_toolbar[0]
        self.reloadbutton = details_toolbar[1]
        self.deletebutton = details_toolbar[2]

    ### interaction callbacks

    def get_behaviour_entry(self):
        # very ugly:
        bh = self.get_behaviour_entry_details()
        bh.__dict__.update(self.get_entry_metadata())
        return bh

    def toggle_detail_widgets(self, observation):
        if self.editbutton.value:
            self.entry_editor.children = [self.summary, self.details]
            self.editbutton.tooltip = "Collapse"
            self.editbutton.icon = icon_minimize #icon_collapse
        else:
            self.entry_editor.children = [self.summary]
            self.editbutton.tooltip = "Expand"
            self.editbutton.icon = icon_edit

    def update_summary_widget(self, observation):
        self.overview_update_callback(
            self.get_behaviour_entry()
        )

    def deletebutton_click(self, b):
        with open(self.filepath, "r+") as json_file:
            store = BehaviourStore(**json.load(json_file))
            store.entries = [entry for entry in store.entries if entry.guid != self.behaviour_entry.guid]

            json_file.seek(0)  # rewind
            json.dump(store, json_file, indent=4, default=lambda x: x.__dict__)
            json_file.truncate()

    def savebutton_click(self, b):
        with open(self.filepath, "r+") as json_file:
            store = BehaviourStore(**json.load(json_file))
            store.entries = [(entry if entry.guid != self.behaviour_entry.guid else self.get_behaviour_entry()) for entry in store.entries]

            json_file.seek(0)  # rewind
            json.dump(store, json_file, indent=4, default=lambda x: x.__dict__)
            json_file.truncate()

    def reloadbutton_click(self, b):
        with open(self.filepath, "r+") as json_file:
            store = BehaviourStore(**json.load(json_file))

            try:
                entry = next(entry for entry in store.entries if entry.guid == self.behaviour_entry.guid)
                self.set_behaviour_entry_details(entry)
            except StopIteration:
                # couldn't find any behaviours with the cached guid... what a problem...
                pass

    def setup_interaction(self):
        ### interaction setup
        self.savebutton.on_click(lambda x: self.savebutton_click(x))
        self.reloadbutton.on_click(lambda x: self.reloadbutton_click(x))
        self.deletebutton.on_click(lambda x: self.deletebutton_click(x))

        # register 'on edit button click'
        self.editbutton.observe(lambda x: self.toggle_detail_widgets(x), 'value')

        # ensure the summary widgets are updated when details change
        for behaviour_edit_widget in self.details_overview:
            behaviour_edit_widget.observe(lambda x: self.update_summary_widget(x), 'value')

    def get_widgets(self):
        return self.entry_editor
