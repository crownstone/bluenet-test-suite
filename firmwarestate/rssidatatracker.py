"""
This is a utility wrapper for the firmware RssiDataTracker class, which pushes its information
to the FirmwareState tracker.
"""
from statistics import mean
import time
import datetime

from BluenetLib import Bluenet
from firmwarecontrol.datatransport import initializeUSB
from firmwarestate import FirmwareState

import matplotlib.pyplot as plt
import matplotlib.animation as animation

class RssiDataTracker:
    def __init__(self, FW):
        self.fw = FW
        self.activeCrownstoneIds = set()
        self.fw.onNewEntryParsed += [lambda e: self.record(e)]

        # keys: frozenset pairs (i,j) (solves all reordering issues)
        # values: pair of lists, containing matching coordinates for
        # the rssi/time data stream
        self.rssitimeseries = dict()

    def record(self, e):
        """
        Add a recorded rssi value for the pair of crowstone ids (i,j).
        """
        if not e.classname == "RssiDataTracker":
            return

        expr = e.valuename.split("_")
        if expr[0] != "rssi" or len(expr) != 3:
            return

        i_j = frozenset({expr[1], expr[2]})
        rssi = float(e.value)

        self.activeCrownstoneIds |= i_j

        if i_j not in self.rssitimeseries:
            self.rssitimeseries[i_j] = [[], []]

        self.rssitimeseries[i_j][0] += [e.time]
        self.rssitimeseries[i_j][1] += [rssi]

    def getLastN(self, i, j, n=1):
        """
        Retrieve the last n Retrieve the FimrwareStateHistoryEntry-s
        for pairs (i,j) and (j,i).
        """
        # reversed iteration is likely faster since look up of recent
        # data will be executed more often
        returnlist = []
        for entry in reversed(self.fw.historylist):
            if self.isRelevant(entry, i, j, True):
                returnlist.add(entry)
            if len(returnlist) >= n:
                return returnlist
        return returnlist

    def getInTimeWindow(self, i, j, t_begin, t_end):
        """
        Retrieve the FimrwareStateHistoryEntry-s for the pairs (i,j) and (j,i)
        which were recorded in the time interval [t_begin, t_end].
        """
        # reversed iteration is likely faster since look up of recent
        # data will be executed more often
        returnlist = []
        for entry in reversed(self.fw.historylist):
            if (entry.time < t_begin
                    and entry.time < t_end
                    and self.isRelevant(entry, i, j, True)):
                returnlist.add(entry)
            if entry.time < t_begin:
                return returnlist
        return returnlist

    def isRelevant(self, fwhistoryentry, i, j, allowSymmetry=False):
        """
        To filter the FirmwareState history list.
        - fwhistoryentry shoud be a FirmwareStateHistoryEntry
        - i, j, should be integers
        - allowSymmetry true will also check reversed i,j.
        """
        return fwhistoryentry.valuename == "rssi_{0}_{1}".format(i, j) or \
               (allowSymmetry and self.isRelevant(fwhistoryentry, j, i, False))


    def avgRssiLastN(self, i, j, n=1):
        return mean(RssiValuesFromListOfEntries(getLastN(i, j, n)))


    def avgRssiInTimeWindow(self, i, j, t_begin, t_end):
        return mean(RssiValuesFromListOfEntries(getInTimeWindow(i, j, t_begin, t_end)))


    def RssiValuesFromListOfEntries(self, listofentries):
        return [float(x.value) for x in listofentries]


class Main:
    def __init__(self):
        self.bluenet = Bluenet()
        self.fwState = FirmwareState()
        initializeUSB(self.bluenet, "ttyACM", range(4))

        self. rssiDataTracker = RssiDataTracker(self.fwState)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.bluenet.stop()

    def run(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)

        def animate(i):
            ax1.clear()

            plotwindow_width = datetime.timedelta(seconds=60)
            time_minimum = datetime.datetime.now() - plotwindow_width
            print("animate called")
            for series_ij, series_time_and_rssi in self.rssiDataTracker.rssitimeseries.items():


                series_time = series_time_and_rssi[0]
                series_rssi = series_time_and_rssi[1]

                # print("plotting : {0}, containing {1} datapoints".format(series_ij, len(series_time)))

                # trim the series
                series_time = [(t-plotwindow_width).timestamp() for t in series_time if t >= time_minimum]
                series_rssi = series_rssi[-len(series_time) : ]

                # print("rssis ({0}): {1}".format(len(series_rssi), series_rssi))

                ax1.plot(series_time, series_rssi)
                break

        ani = animation.FuncAnimation(fig, animate, interval=1000)
        plt.show()

        while True:
            time.sleep(0.5)

if __name__ == "__main__":
    with Main() as m:
        m.run()

