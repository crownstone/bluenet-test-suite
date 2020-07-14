from ipywidgets import VBox

from behaviourstoreeditor.utils import *
from behaviourstoreeditor.icons import *
from behaviourstoreeditor.behaviourstoreserialisation import *

from behaviourstoreeditor.behaviourentry import *
from behaviourstoreeditor.entrymetadata import *
from behaviourstoreeditor.toolbar import *


def BehaviourEntryEditor(behaviour_entry, filepath):
    """
    Returns HBox for Behaviour with additional meta-operations. Concerns exactly one behaviour entry.
    behaviour_entry is a BehaviourEntry
    """
    summary_meta = MetaDataSummary(behaviour_entry, filepath)
    summary_overview, overview_update_callback = BehaviourOverviewSummary(behaviour_entry, filepath)
    summary_toolbar = ToolbarSummary(behaviour_entry, filepath)

    details_meta = MetaDataDetails(behaviour_entry, filepath)
    details_overview, overview_get_behaviour_settings_dict = BehaviourOverviewDetails(behaviour_entry, filepath)
    details_toolbar = ToolbarDetails(behaviour_entry, filepath)

    summary = MakeHBox([summary_meta, summary_overview, summary_toolbar], ['5%', '90%', '5%'])
    details = MakeHBox([details_meta, details_overview, details_toolbar], ['5%', '90%', '5%'])

    entry_editor = VBox([summary], layout=Layout(width='100%'))

    editbutton = summary_toolbar[0]

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
            overview_get_behaviour_settings_dict()
        )

    editbutton.observe(toggle_detail_widgets, 'value')

    for behaviour_edit_widget in details_overview:
        behaviour_edit_widget.observe(update_summary_widget, 'value')

    return entry_editor