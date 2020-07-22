from ipywidgets import Label, Layout

class MetaData:
    def __init__(self, scenario_event, filepath):
        self.eventtime_label = Label(
            disabled=True,
            layout=Layout(width='100%', display='flex', justify_content='center')
        )

        if scenario_event.time is not None:
            self.eventtime_label.value = "{0:02}:{1:02}h".format(scenario_event.time // 3600,
                                                                 (scenario_event.time % 3600) // 60)
        else:
            self.eventtime_label.value = "-"

        self.summary = [self.eventtime_label]
        self.details = []

