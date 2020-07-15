from ipywidgets import VBox

from behaviourstoreeditor.utils import *
from behaviourstoreeditor.icons import *
from behaviourstoreeditor.behaviourstoreserialisation import *

from behaviourstoreeditor.behaviourentry import *
from behaviourstoreeditor.entrymetadata import *
from behaviourstoreeditor.toolbar import *

import json

def BehaviourEntryEditor(behaviour_entry, filepath):
    """
    Returns HBox for Behaviour with additional meta-operations. Concerns exactly one behaviour entry.
    behaviour_entry is a BehaviourEntry
    """
    summary_meta, get_entry_metadata = MetaDataSummary(behaviour_entry, filepath)
    summary_overview, overview_update_callback = BehaviourOverviewSummary(behaviour_entry, filepath)
    summary_toolbar = ToolbarSummary(behaviour_entry, filepath)

    details_meta = MetaDataDetails(behaviour_entry, filepath)
    details_overview, get_behaviour_entry_details = BehaviourOverviewDetails(behaviour_entry, filepath)
    details_toolbar = ToolbarDetails(behaviour_entry, filepath)

    summary = MakeHBox([summary_meta, summary_overview, summary_toolbar], ['5%', '90%', '5%'])
    details = MakeHBox([details_meta, details_overview, details_toolbar], ['5%', '90%', '5%'])

    entry_editor = VBox([summary], layout=Layout(width='100%'))

    editbutton = summary_toolbar[0]
    savebutton = details_toolbar[0]
    reloadbutton = details_toolbar[1]
    deletebutton = details_toolbar[2]

    ### interaction callbacks

    def get_behaviour_entry():
        # very ugly:
        bh = get_behaviour_entry_details()
        bh.__dict__.update(get_entry_metadata())
        return bh

    def toggle_detail_widgets(observation):
        if editbutton.value:
            entry_editor.children = [summary, details]
            editbutton.tooltip = "Collapse"
            editbutton.icon = icon_minimize #icon_collapse
        else:
            entry_editor.children = [summary]
            editbutton.tooltip = "Expand"
            editbutton.icon = icon_edit

    def update_summary_widget(observation):
        overview_update_callback(
            get_behaviour_entry()
        )

    def deletebutton_click(b):
        with open(filepath, "r+") as json_file:
            store = BehaviourStore(**json.load(json_file))
            store.entries = [entry for entry in store.entries if entry.guid != behaviour_entry.guid]

            json_file.seek(0)  # rewind
            json.dump(store, json_file, indent=4, default=lambda x: x.__dict__)
            json_file.truncate()

    def savebutton_click(b):
        with open(filepath, "r+") as json_file:
            store = BehaviourStore(**json.load(json_file))
            store.entries = [(entry if entry.guid != behaviour_entry.guid else get_behaviour_entry()) for entry in store.entries]

            json_file.seek(0)  # rewind
            json.dump(store, json_file, indent=4, default=lambda x: x.__dict__)
            json_file.truncate()

    def reloadbutton_click(b):
        pass

    ### interaction setup
    savebutton.on_click(savebutton_click)
    deletebutton.on_click(deletebutton_click)

    # register 'on edit button click'
    editbutton.observe(toggle_detail_widgets, 'value')

    for behaviour_edit_widget in details_overview:
        behaviour_edit_widget.observe(update_summary_widget, 'value')



    return entry_editor