from ipywidgets import IntSlider, ToggleButtons, Text, Layout, Button, HBox

from scenarioeditor.scenarioserialisation import *

class EventContent:
    def __init__(self, scenario_event, filepath):
        self.scenario_event = scenario_event
        self.filepath = filepath

        self.timepicker_init = 'Initialisation of scenario'
        self.timepicker_run = 'Time of day'

        self.timepicker = ToggleButtons(
            options=[self.timepicker_init, self.timepicker_run],
            value='Time of day',
            description='Executed at:',
            disabled=False,
            button_style='info',
            layout=Layout(width='100%')
        )
        self.timeslider = IntSlider(
            value=9*60*60,
            min=0,
            max=24*60*60,
            step=15*60,
            orientation='horizontal',
            readout=False,
            disabled=False,
            layout=Layout(width='100%')
        )
        self.commandname = Text(
            description='Command:',
            layout=Layout(width='100%')
        )
        self.arguments = Text(
            description='Arguments:',
            placeholder="seperate arguments with ','",
            layout=Layout(width='100%')
        )

        self.summarywidget_left = Button(description="", layout=Layout(width='25%'))
        self.summarywidget_middle = Button(description="uninitialized", layout=Layout(width="auto", padding="0px 5px"))
        self.summarywidget = HBox([self.summarywidget_left, self.summarywidget_middle])

        for widg in self.summarywidget.children:
            widg.style.button_color = 'white'

        self.summary = [self.summarywidget]
        self.details = [self.timepicker, self.timeslider, self.commandname, self.arguments]

        self.setup_interaction()
        self.set(scenario_event)
        
    def get(self):
        s = ScenarioEvent()
        s.time = None if self.timepicker.value == self.timepicker_init else self.timeslider.value
        s.commandname = self.commandname.value
        s.arguments = self.arguments.value
        s.guid = self.scenario_event.guid
        return s

    def set(self, scenario_event):
        self.scenario_event = scenario_event
        self.timepicker.value = self.timepicker_init if scenario_event.time is None else self.timepicker_run
        self.timeslider.value = scenario_event.time or 0
        self.commandname.value = scenario_event.commandname
        self.arguments.value = scenario_event.arguments

    def setup_interaction(self):
        self.timepicker.observe(lambda x: self.update_slider_disabled(), 'value')

        for widg in self.details:
            widg.observe(lambda x: self.update_summary())

    def update_slider_disabled(self):
        if self.timepicker.value == self.timepicker_init:
            self.timeslider.disabled = True
        elif self.timepicker.value == self.timepicker_run:
            self.timeslider.disabled = False

    def update_summary(self):
        color_dict = {
            self.timepicker_init: "#ace3ca",
            self.timepicker_run: "#baa5cf",
            "uninitialized": "red"
        }

        placement_time = self.timeslider.value if self.timepicker.value == self.timepicker_run else 0
        relative_time = int(100 * placement_time / float(24 * 60 * 60))

        self.summarywidget_left.layout.width = str(relative_time) + "%"

        if self.commandname.value:
            self.summarywidget_middle.description = "{0}({1})".format(
                self.commandname.value,
                self.arguments.value
            )
            self.summarywidget_middle.tooltip = self.summarywidget_middle.description

            self.summarywidget_middle.style.button_color = color_dict[self.timepicker.value]
        else:
            self.summarywidget_middle.description = "uninitialized"
            self.summarywidget_middle.style.button_color = color_dict["uninitialized"]
