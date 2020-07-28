import uuid

from crownstone_core.packets.behaviour.BehaviourTypes import BehaviourType
from crownstone_core.packets.behaviour.SwitchBehaviour import SwitchBehaviour
from crownstone_core.packets.behaviour.TwilightBehaviour import TwilightBehaviour
from crownstone_core.packets.behaviour.ExtendedSwitchBehaviour import ExtendedSwitchBehaviour


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
        self.fromfield = 9*60*60
        self.untilfield = 18*60*60
        self.intensityfield = 80
        self.fromuntil_reversed_field = False
        self.typefield = BehaviourType(0).name

    def getBehaviour(self):
        construct = {
            BehaviourType.behaviour.name: lambda: self.populate_switchbehaviour(SwitchBehaviour()),
            BehaviourType.smartTimer.name: lambda: self.populate_twilightbehaviour(ExtendedSwitchBehaviour()),
            BehaviourType.twilight.name: lambda: self.populate_extendedbehaviour(TwilightBehaviour())
        }

        return construct[self.typefield]()

    def populate_basebehaviour(self, b):
        b.setDimPercentage(self.intensityfield)

        fromtime = self.fromfield if not self.fromuntil_reversed_field else self.untilfield
        untiltime = self.untilfield if not self.fromuntil_reversed_field else self.fromfield
        b.setTimeFrom(fromtime // 3600, (fromtime % 3600) // 60)
        b.setTimeTo(untiltime // 3600, (untiltime % 3600) // 60)

        return b

    def populate_switchbehaviour(self, b):
        self.populate_basebehaviour(b)
        b.setPresenceIgnore()
        # TODO: implement specific fields
        return b

    def populate_twilightbehaviour(self, b):
        self.populate_basebehaviour(b)
        return b

    def populate_extendedbehaviour(self, b):
        self.populate_basebehaviour(b)
        # TODO: implement specific fields
        return b


class BehaviourStore():
    def __init__(self, **kwargs):
        if kwargs:
            self.__dict__ = kwargs
            self.entries = [BehaviourEntry(**entry) for entry in self.entries]
            return

        self.entries = []
