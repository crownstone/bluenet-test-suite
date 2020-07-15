from ipywidgets import BoundedIntText, Layout, Textarea, Label, Text


def MetaDataSummary(behaviour_entry, filepath):
    """
    Returns a short summary of the metadata and a getter function that returns the index and guid of the behaviour entry
    """
    indexfield = BoundedIntText(
        value=0,
        min=0,
        max=49,
        step=1,
        tooltip="index in behaviourstore",
        disabled=False,
        layout=Layout(width='100%')
    )

    return [indexfield], lambda: {"index": indexfield.value, "guid": behaviour_entry.guid}

# add GUID field?

def MetaDataDetails(behaviour_entry, filepath):
    guidfield = Text(
        value=str(behaviour_entry.guid),
        disabled=True,
        layout=Layout(width='100%')
    )

    return [guidfield]
