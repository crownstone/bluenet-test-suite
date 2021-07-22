"""
This is a utility wrapper for the firmware RssiDataTracker class, which pushes its information
to the FirmwareState tracker.
"""
from statistics import mean, median
from itertools import combinations, chain
import time
import datetime
import queue

from BluenetLib import Bluenet
from BluenetTestSuite.firmwarecontrol.datatransport import initializeUSB
from BluenetTestSuite.firmwarestate.firmwarestate import FirmwareState

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation


class PingMessage:
    def __init__(self, stamp, send, recv, chan, rss):
        self.timestamp = stamp
        self.sender = send
        self.recipient = recv
        self.channel = chan
        self.rssi = rss

    def __str__(self):
        return ",".join([str(x) for x in [self.timestamp, self.sender, self.recipient, self.channel, self.rssi]])

class RssiStream:
    def __init__(self):
        self.times = []
        self.rssis = []

    def prune(self, time_minimum):
        indx = next(idx for idx, t in enumerate(self.times) if t >= time_minimum)
        self.times = self.times[indx:]
        self.rssis = self.rssis[indx:]

    def put(self, t, r):
        self.times.append(t)
        self.rssis.append(r)

    def printStatus(self):
        print("RssiStream: {0}-{1}, #{2} samples".format(self.times[0], self.times[-1], len(self.rssis)))

class RssiDataTracker:
    def __init__(self, FW):
        self.fw = FW
        self.activeCrownstoneIds = set()

        # receive updates from firmwarestate into self.record
        self.fw.onNewEntryParsed += [lambda e: self.record(e)]

        # if interested in the recorder updates, add a queue to this list.
        # they will all receive the updates.
        self.pingListenerQueues = []

        # keys: frozenset pairs (i,j) (solves all reordering issues)
        # values: pair of lists, containing matching coordinates for
        # the rssi/time data stream
        self.rssitimeseries = dict()

    def addPingListenerQueue(self, q):
        self.pingListenerQueues.append(q)

    def pushPingListenerQueues(self, evnt):
        for q in self.pingListenerQueues:
            q.put(evnt)

    def record(self, e):
        """
        Parse a FW event into a ping message, and push it to listening queues.
        """
        if not e.classname == "RssiDataTracker":
            return

        expr = e.valuename.split("_")
        if expr[0] != "rssi" or len(expr) != 4:
            return

        self.activeCrownstoneIds.add(expr[1])  # sender
        self.activeCrownstoneIds.add(expr[2])  # receiver

        ping = PingMessage(e.time, expr[1], expr[2], int(expr[3]), float(e.value))

        self.pushPingListenerQueues(ping)

    def updateDictsListener(self, ping):
        i_j = frozenset({ping.sender, ping.recipient})

        self.activeCrownstoneIds |= i_j

        if i_j not in self.rssitimeseries:
            # add a first dict mapping the current channel to two empty series
            self.rssitimeseries[i_j] = {ping.channel: {"rssi": [], "time": []}}
        if ping.channel not in self.rssitimeseries[i_j]:
            # add extra dict for new channels
            self.rssitimeseries[i_j][ping.channel] = {"rssi": [], "time": []}

        self.rssitimeseries[i_j][ping.channel]["time"] += [ping.timestamp]
        self.rssitimeseries[i_j][ping.channel]["rssi"] += [ping.rssi]


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
        # initialize components and USB
        self.bluenet = Bluenet()
        self.fwState = FirmwareState()
        initializeUSB(self.bluenet, "ttyACM", range(4))

        # general plotting parameters
        self.trackerfilename = "rssidata.csv"
        self.num_samples_for_median_filter = 5
        self.plotwindow_width = datetime.timedelta(seconds=60)

        # define some run time variables

        # incoming ping messages get split out into this dict for quick iteration.
        # it will be pruned according to the plotting window.
        # using frozensets as primary keys.
        self.stonePairToChannelStreamsDict = dict()

        # queues into which the RssiDataTracker can put its recorded ping messages
        self.pingQueueForLogging = queue.Queue()
        self.pingQueueForPlotting = queue.Queue()

        # set up the tracker
        self.rssiDataTracker = RssiDataTracker(self.fwState)
        self.rssiDataTracker.addPingListenerQueue(self.pingQueueForLogging)
        self.rssiDataTracker.addPingListenerQueue(self.pingQueueForPlotting)

    def __enter__(self):
        self.trackerfile = open(self.trackerfilename, "w+", )

        print("# ", "Tracker file created on: ", datetime.datetime.now(), file=self.trackerfile)
        print("# ", " | ".join([
            "time",
            "sender",
            "recipient",
            "channel",
            "rssi"
        ]), file=self.trackerfile)
        self.trackerfile.flush()

        return self

    def __exit__(self, type, value, traceback):
        # seems to not be called on SIGINT
        print("exiting main")
        self.trackerfile.close()
        self.bluenet.stop()

    def processPingQueueForLogging(self):
        # non blocking processor method
        while not self.pingQueueForLogging.empty():
            ping = self.pingQueueForLogging.get()
            print(ping, file=self.trackerfile)
        self.trackerfile.flush()

    def pruneStonePairToChannelStreamsDict(self, time_minimum):
        for i_j, channelToStreamDict in self.stonePairToChannelStreamsDict.items():
            for channel, rssiStream in channelToStreamDict.items():
                rssiStream.prune(time_minimum)

    def processPingQueueForPlotting(self):
        """
        updates the stonePairToChannelStreamsDict with new ping messages,
        trimming messages that have become stale.

        (non blocking processor method)
        """
        while not self.pingQueueForPlotting.empty():
            ping = self.pingQueueForPlotting.get()

            ij = frozenset([ping.sender, ping.recipient])
            if ij not in self.stonePairToChannelStreamsDict:
                self.stonePairToChannelStreamsDict[ij] = dict()
            if ping.channel not in self.stonePairToChannelStreamsDict[ij]:
                self.stonePairToChannelStreamsDict[ij][ping.channel] = RssiStream()

            self.stonePairToChannelStreamsDict[ij][ping.channel].put(ping.timestamp, ping.rssi)

    def medianFilter(self, list_of_floats, samples_per_median):
        l = list_of_floats
        M = len(l)
        return [
            median(l[max(k-samples_per_median, 0): k] or [l[0]]) for k in range(M)
        ]

    def updatePlotData(self, i, fig, axs_flat):
        now = datetime.datetime.now()
        time_minimum = now - self.plotwindow_width
        self.processPingQueueForPlotting()
        self.pruneStonePairToChannelStreamsDict(time_minimum)

        fig.suptitle("RSSIs for active stones: " + ",".join(["#" + str(id) for id in sorted(self.rssiDataTracker.activeCrownstoneIds)]), fontsize=12)
        myFmt =mdates.DateFormatter('%H:%M:%S')

        # build a mapping from the lowest crownstone ids pair to an ax of the figure, so that
        # we have at most six subplots.
        ax_index = 0
        axs_dict = dict()
        for ij_pair in combinations(sorted(self.rssiDataTracker.activeCrownstoneIds)[0:4], 2):
            axs_dict[frozenset(ij_pair)] = axs_flat[ax_index]
            ax_index += 1
            if ax_index >= len(axs_flat):
                break

        # loop over the available data per crownstone pair
        for i_j, channelToStreamDict in self.stonePairToChannelStreamsDict.items():
            if i_j not in axs_dict:
                # can't plot if there is no axis for it. (will happen for the 5th crownstone)
                break

            # label subplot with the pair id.
            ax = axs_dict[i_j]
            ax.clear()
            ax.set_title(' -> '.join(sorted(i_j)))
            ax.set_xlabel("time(s)")
            ax.set_xlim(time_minimum, now)
            ax.xaxis.set_major_formatter(myFmt) # formats the x-axis ticks
            ax.format_xdata = myFmt # formats the on-hover message box

            # reduce number of ticks on x-axis
            ax.xaxis.set_major_locator(plt.MaxNLocator(3))

            ax.set_ylabel("rssi(dB)")

            # loop over all channels on this pair of crownstones and plot each as a separate line.
            for channel, rssiStream in channelToStreamDict.items():
                ax.plot(rssiStream.times, self.medianFilter(rssiStream.rssis, self.num_samples_for_median_filter),
                        marker='o', markersize=3,
                        label="ch: {0}".format(channel))


    def run(self):
        """
        Method will set up an animation and run it.
        In parallel it will record the data to file.
        """
        fig, axs = plt.subplots(2, 3, sharex=True)
        axs_flat = list(chain.from_iterable(axs))  # for practical reasons have a flattened version of the axs
        ani = animation.FuncAnimation(fig, lambda i: self.updatePlotData(i, fig, axs_flat), interval=250)
        plt.show()

        while True:
            self.processPingQueueForLogging()
            # time.sleep(0.5)

if __name__ == "__main__":
    with Main() as m:
        m.run()

