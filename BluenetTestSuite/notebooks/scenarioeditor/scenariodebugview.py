from ipywidgets import Output, Label, VBox

class ScenarioDebugView:
    def __init__(self, scenario_event, filepath):
        self.output = Output()
        self.guidlabel = Label(F"{scenario_event.guid}")

    def get_widgets(self):
        return VBox(children=[self.guidlabel, self.output])