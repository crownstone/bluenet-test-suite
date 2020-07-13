import uuid

class BehaviourStore():
    def __init__(self):
        self.entries = []

class BehaviourEntry():
    def __init__(self):
        self.guid = uuid.uuid4().hex
        self.fromtime = 9*60*60
        self.untiltime = 18*60*60