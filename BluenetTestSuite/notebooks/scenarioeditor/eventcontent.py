from ipywidgets import IntSlider, ToggleButtons, Text, Layout

from scenarioeditor.scenarioserialisation import *

class EventContent:
    def __init__(self, scenario_event, filepath):
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

        self.set(scenario_event)

        self.summary = []
        self.details = [self.timepicker, self.timeslider, self.commandname, self.arguments]

    def get(self):
        s = ScenarioEvent()
        s.time = None if self.timepicker.value == self.timepicker_init else self.timeslider.value
        s.commandname = self.commandname.value
        s.arguments = self.arguments.value.split(",")
        return s

    def set(self, scenario_event):
        self.timepicker.value = self.timepicker_init if scenario_event.time is None else self.timepicker_run
        self.timeslider.value = scenario_event.time or 0
        self.commandname.value = scenario_event.commandname
        self.arguments.value = scenario_event.arguments

    def update_slider_disabled(self):
        if self.timepicker.value == self.timepicker_init:
            self.timeslider.disabled = True
        elif self.timepicker.value == self.timepicker_run:
            self.timeslider.disabled = False
