"""
This is a utility wrapper for the firmware RssiDataTracker class, which pushes its information
to the FirmwareState tracker.
"""

class RssiDataTracker:
    def __init__(self, FW):
        self.fw = FW
        self.rssivalues = dict()

    def record(self, i, j, rssi):
        """
        Add a recorded rssi value for the pair of crowstone ids (i,j).
        """
        pass

    def getAverageLastValues(self, i, j, n = 1):
        """
        Retrieve the average of the last n recorded rssi values for pairs (i,j) and (j,i).
        """
        pass

    def getAverageInTimeWindow(self, i,j, t_start, t_end):
        """
        Retrieve the average of the the recorded rssi values for the pairs (i,j) and (j,i)
        which were recorded in the time interval [t_start, t_end].
        """
        pass

    def isRelevant(self, fwhistoryentry, i,j, allowSymmetry=False):
        """
        To filter the FirmwareState history list.
        """