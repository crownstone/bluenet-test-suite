
class RssiDataPoint:
    def __init__(self, stamp, send, recv, chan, rss):
        self.timestamp = stamp
        self.sender = send
        self.receiver = recv
        self.channel = chan
        self.rssi = rss

    def __str__(self):
        return ",".join([str(x) for x in [self.timestamp, self.sender, self.receiver, self.channel, self.rssi]])


class RssiStream:
    def __init__(self, sender, receiver):
        self.receiver = receiver
        self.sender = sender
        self.times = []
        self.rssis = []

    def removeOldEntries(self, time_minimum):
        try:
            indx = next(idx for idx, t in enumerate(self.times) if t >= time_minimum)
            self.times = self.times[indx:]
            self.rssis = self.rssis[indx:]
        except StopIteration:
            # nothing to trim, that's ok.
            pass

    def addNewEntry(self, timestamp, rssivalue):
        self.times.append(timestamp)
        self.rssis.append(rssivalue)

    def status(self):
        return F"RssiStream ({self.sender} -> {self.receiver}) time window {self.times[0]}-{self.times[-1]}, {len(self.rssis)} samples"

class NearestStream:
    def __init__(self, sender):
        self.sender = sender
        self.times = []
        self.rssis = []
        self.receivers = []

    def removeOldEntries(self, time_minimum):
        try:
            indx = next(idx for idx, t in enumerate(self.times) if t >= time_minimum)
            self.times = self.times[indx:]
            self.rssis = self.rssis[indx:]
        except StopIteration:
            # nothing to trim, that's ok.
            pass

    def addNewEntry(self, timestamp, rssivalue, receiver):
        self.times.append(timestamp)
        self.rssis.append(rssivalue)
        self.receivers.append(receiver)

    def status(self):
        return F"NearestStream ({self.sender}) time window {self.times[0]}-{self.times[-1]}, {len(self.rssis)} samples"