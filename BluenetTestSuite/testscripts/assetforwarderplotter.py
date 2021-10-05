"""
This script monitors the UART output of the asset forwarder component:

A list of assets is defined.
Two filters are constructed, which both represent the list of assets.
The filters are identical, except for the output type, which is forward MAC resp. SID.
The filters are commited into the mesh.

From that point on, the crownstone that is connected via UART will provide the events:
- 10108: Asset Rssi Data
- 10109: Nearest Crownstone Update
- 10110: Nearest Crownstone TimeOut

These incoming events are linked to the original list of assets by their index and they are timestamped.
At each incoming event, the status can be validated:
- If a Nearest Crownstone Update is received, does it match with the Nearest Crownstone
  according to the Asset Rssi Data events?
  (Possibly allowing accomodation time and rssi margin)
- If a Nearest Crownstone TimeOut is received, how long ago was the last Asset Rssi Data event?


All of this can be displayed in a rolling graph by simply plotting per asset the time series of each crownstones
rssi values received through the Asset Rssi Data events and annotating the winner transitions and timeouts etc.
- winner: think line
- timed out: dotted/dashed
- other: normal line


TODO: currently only one asset is supported.
"""
from functools import singledispatch
import datetime
from queue import Queue
from sys import stdout
from threading import Thread

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
import matplotlib


matplotlib.use('TkAgg')

from crownstone_uart import UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics

from crownstone_uart.core.uart.UartTypes import UartRxType
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket

from crownstone_uart.core.uart.uartPackets.AssetIdReport import AssetIdReport
from crownstone_uart.core.uart.uartPackets.AssetMacReport import AssetMacReport

from BluenetTestSuite.utils.setup import *
from BluenetTestSuite.utils.rssistream import *
from BluenetTestSuite.utils.filterexamples import *
from BluenetTestSuite.utils.filtercommands import *



class PlotterQueueObject:
    """
    Used in the plotter queue
    """
    def __init__(self, msg):
        self.msg = msg
        self.timestamp = datetime.datetime.now()

class NearestCrownstoneAlgorithmPlotter:
    """
    This class is responsible for decoupling the Uart thread from the plotting thread by means of a queue.
    Further it passively keeps track of the plotting information. How to visualize the data is left to the user
    of the class.
    """

    def __init__(self, plottingtimewindow_seconds, refreshRateMs):
        self.assetSidRssiStreams = []             # a list of NearestStream objects based on incoming AssetMacReport messages.
        self.assetMacRssiStreams = []  # a list of NearestStream objects based on incoming AssetSidReport messages.
        self.plottingQueue = Queue()
        self.loggingQueue = Queue()

        self.plotwindow_width = datetime.timedelta(seconds=plottingtimewindow_seconds)
        self.refreshRateMs = refreshRateMs

        # a callable that translates integers to pyplot colors. Other qualitative palletes:
        # ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c']
        self.colormap = plt.get_cmap('tab10')


    def putMessageOnQueue(self, msg):
        self.plottingQueue.put(PlotterQueueObject(msg))

    def updatePlotData(self, i, fig, axs_flat):
        """
        Processes queue for plotting.
        Remove old messages.
        Plot.
        """
        try:
            self.processPlottingQueue()
            self.removeOldEntriesFromStreams()
            self.plot(i, fig, axs_flat)
        except Exception as e:
            print(e)
            raise e


    def plot(self, i, fig, axs_flat):
        # title and format
        fig.suptitle(self.getTitle(), fontsize=12)

        myFmt = mdates.DateFormatter('%H:%M:%S')

        past, now = self.getTimeWindow()

        for ax in axs_flat:
            # each ax is a subplot that presents one asset.
            # TODO: filter streams per asset.

            ax.clear()
            ax.set_title(F"AssetId # todo ")

            # x axis
            ax.set_xlabel("time (H:M:S)")
            ax.xaxis.set_major_formatter(myFmt)  # formats the x-axis ticks
            ax.format_xdata = myFmt  # formats the on-hover message box
            ax.xaxis.set_major_locator(plt.MaxNLocator(3))  # reduce number of ticks on x-axis
            ax.set_xlim(past, now)

            # y axis
            ax.set_ylabel("rssi(dB)")
            ax.set_ylim(-80, -10)

            # plot the MAC streams (as lines)
            for stream in self.assetMacRssiStreams:
                ax.plot(stream.times, stream.rssis,
                        marker='o', markersize=3, label=f"MAC cs #{stream.receiver}",
                        linestyle='-', color=self.colormap(stream.receiver))

            # plot the SID streams (as markers)
            for stream in self.assetSidRssiStreams:
                ax.plot(stream.times, stream.rssis,
                        marker='o', markersize=8, fillstyle='none', label=f"SID cs #{stream.receiver}",
                        linestyle='',color=self.colormap(stream.receiver))

            ax.legend()



    def processPlottingQueue(self):
        """
        Updates the rssi stream according to the new events.
        Should be called before each frame update.

        Terminates when the plotting queue is empty
        """
        while not self.plottingQueue.empty():
            plottingQueueObject = self.plottingQueue.get()
            handlePlottingQueueObject(plottingQueueObject.msg, plottingQueueObject.timestamp, self)

    def getTimeWindow(self):
        now = datetime.datetime.now()
        return now - self.plotwindow_width, now

    def removeOldEntriesFromStreams(self):
        past, now = self.getTimeWindow()

        for stream in self.assetMacRssiStreams:
            stream.removeOldEntries(past)
        for stream in self.assetSidRssiStreams:
            stream.removeOldEntries(past)

    def getTitle(self):
        return "Nearest Crownstone Algorithm Plot"


@singledispatch
def handlePlottingQueueObject(msg, timestamp: datetime.datetime, plotter: NearestCrownstoneAlgorithmPlotter):
    raise NotImplementedError("Only available for arguments with registered overridde")

@handlePlottingQueueObject.register
def handleAssetMacRssiReport(msg : AssetMacReport, timestamp: datetime.datetime, plotter: NearestCrownstoneAlgorithmPlotter):
    try:
        sender = msg.assetMacAddress
        receiver = msg.crownstoneId
        rssi = msg.rssi
        channel = msg.channel

        ### update the asset rssi stream for this (asset,crownstone) pair
        # find the nearest stream for this sender->receiver
        stream = next(filter(lambda s: s.sender == sender and s.receiver == receiver, plotter.assetMacRssiStreams), None)

        # create one if necessary
        if stream is None:
            stream = RssiStream(sender, receiver)
            plotter.assetMacRssiStreams.append(stream)

        stream.addNewEntry(timestamp, rssi)
    except Exception as e:
        print(e)
        raise e

@handlePlottingQueueObject.register
def handleAssetSidRssiReport(msg : AssetSidReport, timestamp: datetime.datetime, plotter: NearestCrownstoneAlgorithmPlotter):
    try:
        sender = msg.shortAssetId
        receiver = msg.crownstoneId
        rssi = msg.rssi
        channel = msg.channel

        ### update the asset rssi stream for this (asset,crownstone) pair
        # find the nearest stream for this sender->receiver
        stream = next(filter(lambda s: s.sender == sender and s.receiver == receiver, plotter.assetSidRssiStreams), None)

        # create one if necessary
        if stream is None:
            stream = RssiStream(sender, receiver)
            plotter.assetSidRssiStreams.append(stream)

        stream.addNewEntry(timestamp, rssi)
    except Exception as e:
        print(e)
        raise e



class NearestCrownstoneLogger(Thread):
    """
    Thread to decouple logging incoming messages by means of a queue.

    See putMessageOnQueue.
    """
    def __init__(self, outputfilename=None):
        super(NearestCrownstoneLogger, self).__init__()
        self.loggingQueue = Queue()

        self.trackerfilename = outputfilename
        self.trackerfile = None
        self.isRunning = True

    def putMessageOnQueue(self, msg):
        self.loggingQueue.put(msg)

    def processLoggingQueue(self):
        """
        logs the queued items to the trackerfile.
        terminates when the queue is empty.
        """
        self.open_logging_file()

        while not self.loggingQueue.empty():
            evt = self.loggingQueue.get()
            print("plotter log:", evt, file=self.trackerfile)

        self.close_logging_file()

    def run(self):
        self.open_logging_file()
        print("# ", "Tracker file created on: ", datetime.datetime.now(), file=self.trackerfile)
        self.close_logging_file()
        time.sleep(0.2)

        while self.isRunning:
            self.processLoggingQueue()
            time.sleep(0.2)

    def open_logging_file(self):
        # default to stdout if no filename is given.
        self.trackerfile = open(self.trackerfilename, "w+", ) if self.trackerfilename else stdout

    def close_logging_file(self):
        self.trackerfile.flush()

        if self.trackerfilename is not None:
            self.trackerfile.close()




class FilterManager:
    def __init__(self, macaddresslist, shouldloadfilters):
        self.macadresses = macaddresslist
        self.trackingfilters = []
        self.trackingfilters.append(filterExactMacInForwarderMacOut(self.macadresses))
        self.trackingfilters.append(filterExactMacInForwarderShortIdOut(self.macadresses))

        self.shouldloadfilters = shouldloadfilters

    def loadfilters(self):
        if not self.shouldloadfilters:
            return

        masterCrc = removeAllFilters()

        for fid, fltr in enumerate(self.trackingfilters):
            fltr.setFilterId(fid)

        masterCrc = uploadFilters(self.trackingfilters)
        finalizeFilterUpload(masterCrc,version=10)
        getStatus()



class Main:
    def __init__(self, outputfilename = None, plottingtimewindow_seconds=60, refreshRateMs=250, macaddresslist=[], loadfilters=False):
        """
        Setup filters Logger and plotter to visualise various nearest crownstone algorithm statistics.
        """
        # initialize uart
        self.crownstoneUart = setupCrownstoneUart()
        self.crownstoneLogs = setupCrownstoneLogs()

        self.uartMsgSubscription = UartEventBus.subscribe(SystemTopics.uartNewMessage, lambda msg: self.uartmsghandler(msg))

        # general plotting parameters
        self.logger = NearestCrownstoneLogger(outputfilename)
        self.plotter = NearestCrownstoneAlgorithmPlotter(plottingtimewindow_seconds, refreshRateMs)
        self.filtermanager = FilterManager(macaddresslist, loadfilters)

    def __enter__(self):
        self.logger.start()
        self.filtermanager.loadfilters()

        return self

    def __exit__(self, type, value, traceback):
        self.logger.isRunning = False
        self.crownstoneUart.stop()

    ### incoming Uart messages

    def uartmsghandler(self, msg: UartMessagePacket):
        """
        Construct object from uart message and put it on the logger/plotter queues.
        """
        # try:
        typemap = {
            UartRxType.ASSET_MAC_RSSI_REPORT: AssetMacReport,
            UartRxType.ASSET_SID_RSSI_REPORT: AssetSidReport,
        }

        packettype = typemap.get(msg.opCode, None)

        if packettype is not None:
            print(f"Received {packettype} {str(msg.opCode)}: {msg.payload}")
            packet = packettype()
            packet.deserialize(msg.payload)
            self.logger.putMessageOnQueue(packet)
            self.plotter.putMessageOnQueue(packet)
        # except Exception as e:
        #     print(e)


    def run(self):
        """
        Method will set up an animation and run it.
        In parallel it will record the data to file.
        """
        fig, axs = plt.subplots(1, 1, sharex=True)

        # axs is a 2d list. 1d lists are easier to iterate, so thats axs_flat.
        axs_flat = [axs] # 1,1  results in axs not being wrapped in a list...
        # axs_flat = list(chain.from_iterable(axs))

        ani = animation.FuncAnimation(fig,
                                      lambda i: self.plotter.updatePlotData(i, fig, axs_flat),
                                      interval=self.plotter.refreshRateMs)
        # plt.ion()
        plt.show()

        try:
            while True:
                self.logger.processLoggingQueue()
                time.sleep(0.1)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    setupLogLevel(info=True)
    with Main(outputfilename=None, plottingtimewindow_seconds=3*60, macaddresslist =getMacList(), loadfilters=True) as m:
        m.run()

