"""
This is a utility wrapper for the firmware RssiDataTracker class, which pushes its information
to the FirmwareState tracker.
"""
from statistics import mean, median
from itertools import combinations, chain
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
        if expr[0] != "rssi" or len(expr) != 4:
            return

        sender = expr[1]
        recipient = expr[2]
        channel = int(expr[3])
        rssi = float(e.value)

        i_j = frozenset({sender, recipient})

        self.activeCrownstoneIds |= i_j

        if i_j not in self.rssitimeseries:
            # add a first dict mapping the current channel to two empty series
            self.rssitimeseries[i_j] = {channel: {"rssi":[], "time":[]}}
        if channel not in self.rssitimeseries[i_j]:
            # add extra dict for new channels
            self.rssitimeseries[i_j][channel] = {"rssi": [], "time": []}

        self.rssitimeseries[i_j][channel]["time"] += [e.time]
        self.rssitimeseries[i_j][channel]["rssi"] += [rssi]

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

    def medianFilter(self, list_of_floats, samples_per_median):
        l = list_of_floats
        M = len(l)
        return [
            median(l[max(k-samples_per_median, 0): k] or [l[0]]) for k in range(M)
        ]

    def run(self):
        fig, axs = plt.subplots(2, 3, sharex=True)
        axs_flat = list(chain.from_iterable(axs)) # for practical reasons have a flattened version of the axs

        # general plotting parameters
        num_samples_for_median_filter = 1
        plotwindow_width = datetime.timedelta(seconds=60)
        time_minimum = datetime.datetime.now() - plotwindow_width

        def animate(i):
            # build a mapping from the lowest crownstone ids pair to an ax of the figure
            ax_index = 0
            axs_dict = dict()
            for ij_pair in combinations(sorted(self.rssiDataTracker.activeCrownstoneIds)[0:4], 2):
                axs_dict[frozenset(ij_pair)] = axs_flat[ax_index]
                ax_index += 1
                if ax_index >= len(axs_flat):
                    break

            # loop over the available data per crownstone pair
            for series_ij, channel_to_series_time_and_rssi in self.rssiDataTracker.rssitimeseries.items():
                if series_ij not in axs_dict:
                    # can't plot if there is no axis for it. (will happen for the 5th crownstone)
                    break

                # label subplot with the pair id.
                ax = axs_dict[series_ij]
                ax.clear()
                ax.set_xlabel("time(s)")
                ax.set_ylabel("rssi(dB)" + "->".join(series_ij))

                # loop over all channels on this pair of crownstones and plot each as a separate line.
                for channel, time_rssi_series_dict in channel_to_series_time_and_rssi.items():
                    series_time = time_rssi_series_dict["time"]
                    series_rssi = time_rssi_series_dict["rssi"]

                    # trim the series to fit the time window
                    series_time = [(t-time_minimum).total_seconds() for t in series_time if t >= time_minimum]
                    series_rssi = self.medianFilter(series_rssi[-len(series_time) : ], num_samples_for_median_filter)

                    ax.plot(series_time, series_rssi,
                             marker='o', markersize=3,
                             label="ch: {0}".format(channel))

                # ax.legend()

        ani = animation.FuncAnimation(fig, animate, interval=250)
        plt.show()

        while True:
            time.sleep(0.5)

if __name__ == "__main__":
    with Main() as m:
        m.run()

