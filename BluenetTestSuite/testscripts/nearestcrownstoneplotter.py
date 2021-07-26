"""
This is a utility wrapper for the firmware RssiDataTracker class, which pushes its information
to the FirmwareState tracker.
"""
from itertools import combinations, chain, combinations_with_replacement
from functools import singledispatch
import time
import datetime
from queue import Queue
from sys import stdout
from threading import Thread

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
import matplotlib
matplotlib.use('TkAgg')

from BluenetTestSuite.utils.setup import *
from BluenetTestSuite.utils.rssistream import *


from crownstone_uart import UartEventBus
from crownstone_uart.topics.SystemTopics import SystemTopics

from crownstone_uart.core.uart.UartTypes import UartRxType
from crownstone_uart.core.uart.uartPackets.UartMessagePacket import UartMessagePacket

from crownstone_uart.core.uart.uartPackets.NearestCrownstones import NearestCrownstoneTrackingUpdate
from crownstone_uart.core.uart.uartPackets.NearestCrownstones import NearestCrownstoneTrackingTimeout
from crownstone_uart.core.uart.uartPackets.AssetMacReport import AssetMacReport


class PlotterQueueObject:
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
        self.rssistreams = [] # a list of RssiStream objects, sender == asset, receiver == crownstoneid
        self.plottingQueue = Queue()
        self.loggingQueue = Queue()

        self.plotwindow_width = datetime.timedelta(seconds=plottingtimewindow_seconds)
        self.refreshRateMs = refreshRateMs

    def putMessageOnQueue(self, msg):
        self.plottingQueue.put(PlotterQueueObject(msg))

    def updatePlotData(self, i, fig, axs_flat):
        """
        Processes queue for plotting.
        Remove old messages.
        Plot.
        """
        self.processPlottingQueue()
        self.removeOldEntriesFromStreams()
        self.plot(i, fig, axs_flat)

    def plot(self, i, fig, axs_flat):
        # title and format
        fig.suptitle(self.getTitle(), fontsize=12)

        # for ax in axs_flat:
        #     ax.set_title("hi")
        #     ax.plot()

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
            ax.set_ylim(-10, -80)

            for stream in self.rssistreams:
                ax.plot(stream.times, stream.rssis,
                        marker='o', markersize=3,
                        label=f"#{stream.receiver}")

            ax.legend()
            # ax.plot()

        return

    def processPlottingQueue(self):
        """
        Updates the rssi stream according to the new events.
        Should be called before each frame update.

        Terminates when the plotting queue is empty
        """
        print(F" *** Processing Plotting Queue *** ({self.plottingQueue.qsize()})")
        while not self.plottingQueue.empty():
            plottingQueueObject = self.plottingQueue.get()
            handlePlottingQueueObject(plottingQueueObject.msg, plottingQueueObject.timestamp, self)

    def getTimeWindow(self):
        now = datetime.datetime.now()
        return now - self.plotwindow_width, now

    def removeOldEntriesFromStreams(self):
        past, now = self.getTimeWindow()

        for stream in self.rssistreams:
            stream.removeOldEntries(past)

    def getTitle(self):
        return "Nearest Crownstone Algorithm Plot"


@singledispatch
def handlePlottingQueueObject(msg, timestamp: datetime.datetime, plotter: NearestCrownstoneAlgorithmPlotter):
    raise NotImplementedError("Only available for arguments with registered overridde")

@handlePlottingQueueObject.register
def handleNearestCrowntoneUpdate(msg : NearestCrownstoneTrackingUpdate, timestamp: datetime.datetime, plotter: NearestCrownstoneAlgorithmPlotter):
    print("NearestCrownstoneTrackingUpdate ", timestamp)
    sender = msg.assetId
    receiver = msg.crownstoneId
    rssi = msg.rssi.val # TODO: adjust when new serialization is done
    channel = msg.channel

    stream = next(filter(lambda s: s.sender == sender and s.receiver == receiver, plotter.rssistreams), None)

    if stream is None:
        print("adding new stream object for pair: ", sender, receiver)
        stream = RssiStream(sender, receiver)
        plotter.rssistreams.append(stream)

    stream.addNewEntry(timestamp, rssi)


@handlePlottingQueueObject.register
def handleNearestCrownstoneTimeOut(msg : NearestCrownstoneTrackingTimeout, plotter: NearestCrownstoneAlgorithmPlotter):
    print("NearestCrownstoneTrackingTimeout")

@handlePlottingQueueObject.register
def handleAssetMacRssiReport(msg : AssetMacReport, plotter: NearestCrownstoneAlgorithmPlotter):
    print("AssetMacReport")




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
        print(F" *** Processing Logging Queue *** ({self.loggingQueue.qsize()})")
        self.open_logging_file()

        while not self.loggingQueue.empty():
            evt = self.loggingQueue.get()
            print(evt, file=self.trackerfile)

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

class Main:
    def __init__(self, outputfilename = None, plottingtimewindow_seconds=60, refreshRateMs=250):
        # initialize uart
        self.crownstoneUart = setupCrownstoneUart()
        self.crownstoneLogs = setupCrownstoneLogs()

        self.uartMsgSubscription = UartEventBus.subscribe(SystemTopics.uartNewMessage, lambda msg: self.uartmsghandler(msg))

        # general plotting parameters
        self.logger = NearestCrownstoneLogger(outputfilename)
        self.plotter = NearestCrownstoneAlgorithmPlotter(plottingtimewindow_seconds, refreshRateMs)

    def __enter__(self):
        self.logger.start()
        return self

    def __exit__(self, type, value, traceback):
        self.logger.isRunning = False
        self.crownstoneUart.stop()

    ### incoming Uart messages

    def uartmsghandler(self, msg: UartMessagePacket):
        """
        Construct object from uart message and put it on the logger/plotter queues.
        """
        typemap = {
            UartRxType.NEAREST_CROWNSTONE_TRACKING_UPDATE: NearestCrownstoneTrackingUpdate,
            UartRxType.NEAREST_CROWNSTONE_TRACKING_TIMEOUT: NearestCrownstoneTrackingTimeout,
            UartRxType.ASSET_MAC_RSSI_REPORT: UartRxType.ASSET_MAC_RSSI_REPORT
        }

        packettype = typemap.get(msg.opCode, None)

        if packettype is not None:
            print(f"Received {packettype} {str(msg.opCode)}: {msg.payload}")
            packet = packettype()
            packet.setPacket(msg.payload)
            self.logger.putMessageOnQueue(packet)
            self.plotter.putMessageOnQueue(packet)


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

        while True:
            self.logger.processLoggingQueue()
            time.sleep(0.1)

if __name__ == "__main__":
    with Main(outputfilename=None, plottingtimewindow_seconds=60) as m:
        m.run()

