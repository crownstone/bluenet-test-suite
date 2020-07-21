import uuid

class ScenarioEvent():
    """
    To serialize/deserialize with json
    """
    def __init__(self, **kwargs):
        if kwargs:
            self.__dict__ = kwargs
            return

        self.guid = uuid.uuid4().hex
        self.time = None
        self.commandname = "wait"
        self.arguments = []


class ScenarioDescription:
    def __init__(self, **kwargs):
        if kwargs:
            self.__dict__ = kwargs
            self.events = [ScenarioEvent(**evt) for evt in self.events]
            return

        self.events = []
