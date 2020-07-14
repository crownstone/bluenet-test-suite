import uuid

class BehaviourStore():
    def __init__(self):
        self.entries = []

class BehaviourEntry():
    """
    To serialize/deserialize with json:
    bh = BehaviourEntry()  # construct default values
    bh_s = json.dumps(bh.__dict__)
    bh_l = BehaviourEntry(**json.loads(bh_s))

    then bh.__dict__ == bh_l.__dict__
    """
    def __init__(self, **kwargs):
        if kwargs:
            self.__dict__ = kwargs
            return

        self.guid = uuid.uuid4().hex
        self.index = 0
        self.fromtime = 9*60*60
        self.untiltime = 18*60*60