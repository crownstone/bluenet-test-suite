from ipywidgets import Layout, HBox
from ipywidgets import IntRangeSlider, IntSlider, BoundedIntText
from ipywidgets import Button, ToggleButtons
from ipywidgets import Checkbox

def BehaviourOverviewSummary():
    """
    Returns list of widgets for single line description of a behaviour,
    and a callback taking in a behaviour description dict to update its value.
    """
    color_dict = {
        'Switch': "lightgreen",
        'ExtendedSwitch': "lightblue",
        'Twilight': "#DADADA"
    }

    no_color = "#FFFFFF"

    summarywidget_left = Button(description="", layout=Layout(width='25%'))
    summarywidget_middle = Button(description="uninitialized", layout=Layout(width='50%'))
    summarywidget_right = Button(description="", layout=Layout(width='25%'))

    summarywidget_left.style.button_color = no_color
    summarywidget_middle.style.button_color = no_color
    summarywidget_right.style.button_color = no_color

    summarywidget = HBox([summarywidget_left, summarywidget_middle, summarywidget_right])

    def update_summary(behaviour_settings_dict):
        relative_min = int(100 * behaviour_settings_dict['from'] / float(24 * 60 * 60))
        relative_max = int(100 * behaviour_settings_dict['until'] / float(24 * 60 * 60))
        summarywidget_left.layout.width = str(relative_min) + "%"
        summarywidget_middle.layout.width = str(relative_max - relative_min) + "%"
        summarywidget_right.layout.width = str(100 - relative_max) + "%"

        summarywidget_middle.description = "{0} ({1}%)".format(
            behaviour_settings_dict['type'],
            behaviour_settings_dict['intensity']
        )

        active_color = color_dict[behaviour_settings_dict['type']]
        not_reversed = not behaviour_settings_dict['fromuntil_reversed']
        summarywidget_left.style.button_color = no_color if not_reversed else active_color
        summarywidget_middle.style.button_color = active_color if not_reversed else no_color
        summarywidget_right.style.button_color = no_color if not_reversed else active_color

    return [summarywidget], update_summary


def BehaviourOverviewDetails():
    """
    Returns list of widgets for multi line description of a behaviour
    """
    fromuntilfield = IntRangeSlider(
        value=[9 * 60 * 60, 18 * 60 * 60],
        min=0,
        max=24 * 60 * 60,
        step=60,
        disabled=False,
        orientation='horizontal',
        readout=False,
        readout_format='.1f',
        layout=Layout(width='100%')
    )

    fromfield = BoundedIntText(
        value=9 * 60 * 60,
        min=0,
        max=24 * 60 * 60,
        description='From:',
        disabled=False,
    )

    untilfield = BoundedIntText(
        value=18 * 60 * 60,
        min=0,
        max=24 * 60 * 60,
        description='Until:',
        disabled=False,
    )

    def on_range_field_change(change):
        fromval, untilval = change['new']
        fromfield.value = fromval
        untilfield.value = untilval

    def on_from_field_change(change):
        prev_from_until = fromuntilfield.value
        next_from_until = (change['new'], prev_from_until[1])

        if next_from_until[0] <= next_from_until[1]:
            fromuntilfield.value = next_from_until

    def on_until_field_change(change):
        prev_from_until = fromuntilfield.value
        next_from_until = (prev_from_until[0], change['new'])

        if next_from_until[0] <= next_from_until[1]:
            fromuntilfield.value = next_from_until

    fromuntilfield.observe(on_range_field_change, names='value')
    fromfield.observe(on_from_field_change, names='value')
    untilfield.observe(on_until_field_change, names='value')

    intensityfield = IntSlider(
        value=100,
        min=0,
        max=100,
        description='Intensity:',
        disabled=False,
        orientation='horizontal',
    )

    # only necessary because the range slider doesn't include reversed ranges...
    fromuntil_reversed_field = Checkbox(
        value=False,
        description='Midnight:',
        tooltip='Reverses from/until times when checked',
        disabled=False,
        indent=False
    )

    typefield = ToggleButtons(
        options=['Switch', 'ExtendedSwitch', 'Twilight'],
        description='Type:',
        disabled=False,
        button_style='info',
        layout=Layout(width='100%')
    )

    def get_behaviour_settings_dict():
        settings = dict()
        settings['intensity'] = intensityfield.value
        settings['type'] = typefield.value
        settings['fromuntil_reversed'] = fromuntil_reversed_field.value
        settings['from'] = fromfield.value
        settings['until'] = untilfield.value
        return settings

    return [fromuntilfield, fromfield, untilfield,
            intensityfield, fromuntil_reversed_field, typefield], get_behaviour_settings_dict

