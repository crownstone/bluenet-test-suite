from ipywidgets import BoundedIntText, Layout


def MetaDataSummary(behaviour_entry, filepath):
    indexfield = BoundedIntText(
        value=0,
        min=0,
        max=49,
        step=1,
        tooltip="index in behaviourstore",
        disabled=False,
        layout=Layout(width='100%')
    )

    return [indexfield]

# add GUID field?

def MetaDataDetails(behaviour_entry, filepath):
    return []
