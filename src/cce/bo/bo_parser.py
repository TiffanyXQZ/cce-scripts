from __future__ import division
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from statistics import mode
from statsmodels.distributions.empirical_distribution import ECDF

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree


def parse_time_ns(tm):
    if tm.endswith('ns'):
        return int(tm[:-4])
    raise ValueError(tm)


## FiveTuple
class FiveTuple(object):
    ## class variables
    ## @var sourceAddress
    #  source address
    ## @var destinationAddress
    #  destination address
    ## @var protocol
    #  network protocol
    ## @var sourcePort
    #  source port
    ## @var destinationPort
    #  destination port
    ## @var __slots__
    #  class variable list
    __slots__ = ['sourceAddress', 'destinationAddress', 'protocol', 'sourcePort', 'destinationPort']

    def __init__(self, el):
        '''The initializer.
        @param self The object pointer.
        @param el The element.
        '''
        self.sourceAddress = el.get('sourceAddress')
        self.destinationAddress = el.get('destinationAddress')
        self.sourcePort = int(el.get('sourcePort'))
        self.destinationPort = int(el.get('destinationPort'))
        self.protocol = int(el.get('protocol'))


## Histogram
class Histogram(object):
    ## class variables
    ## @var bins
    #  histogram bins
    ## @var nbins
    #  number of bins
    ## @var number_of_flows
    #  number of flows
    ## @var __slots__
    #  class variable list
    __slots__ = 'bins', 'nbins', 'number_of_flows'

    def __init__(self, el=None):
        ''' The initializer.
        @param self The object pointer.
        @param el The element.
        '''
        self.bins = []
        if el is not None:
            # self.nbins = int(el.get('nBins'))
            for bin in el.findall('bin'):
                self.bins.append((float(bin.get("start")), float(bin.get("width")), int(bin.get("count"))))


## Flow
class Flow(object):
    ## class variables
    ## @var flowId
    #  delay ID
    ## @var delayMean
    #  mean delay
    ## @var packetLossRatio
    #  packet loss ratio
    ## @var rxBitrate
    #  receive bit rate
    ## @var txBitrate
    #  transmit bit rate
    ## @var fiveTuple
    #  five tuple
    ## @var packetSizeMean
    #  packet size mean
    ## @var probe_stats_unsorted
    #  unsirted probe stats
    ## @var hopCount
    #  hop count
    ## @var flowInterruptionsHistogram
    #  flow histogram
    ## @var rx_duration
    #  receive duration
    ## @var __slots__
    #  class variable list
    __slots__ = ['flowId', 'delayMean', 'packetLossRatio', 'rxBitrate', 'txBitrate',
                 'fiveTuple', 'packetSizeMean', 'probe_stats_unsorted',
                 'hopCount', 'flowInterruptionsHistogram', 'rx_duration', 'rxPackets']

    def __init__(self, flow_el):
        ''' The initializer.
        @param self The object pointer.
        @param flow_el The element.
        '''
        self.flowId = int(flow_el.get('flowId'))
        rxPackets = int(flow_el.get('rxPackets'))
        txPackets = int(flow_el.get('txPackets'))
        tx_duration = float(
            int(flow_el.get('timeLastRxPacket')[:-4]) - int(flow_el.get('timeFirstTxPacket')[:-4])) * 1e-9
        rx_duration = float(
            int(flow_el.get('timeLastRxPacket')[:-4]) - int(flow_el.get('timeFirstRxPacket')[:-4])) * 1e-9
        self.rx_duration = rx_duration
        self.probe_stats_unsorted = []
        if rxPackets:
            self.hopCount = float(flow_el.get('timesForwarded')) / rxPackets + 1
            self.rxPackets = rxPackets
        else:
            self.hopCount = -1000
        if rxPackets:
            self.delayMean = float(flow_el.get('delaySum')[:-4]) / rxPackets * 1e-9
            self.packetSizeMean = float(flow_el.get('rxBytes')) / rxPackets
        else:
            self.delayMean = None
            self.packetSizeMean = None
        if rx_duration > 0:
            self.rxBitrate = int(flow_el.get('rxBytes')) * 8 / rx_duration
        else:
            self.rxBitrate = None
        if tx_duration > 0:
            self.txBitrate = int(flow_el.get('txBytes')) * 8 / tx_duration
        else:
            self.txBitrate = None
        lost = float(flow_el.get('lostPackets'))
        # print "rxBytes: %s; txPackets: %s; rxPackets: %s; lostPackets: %s" % (flow_el.get('rxBytes'), txPackets, rxPackets, lost)
        if rxPackets == 0:
            self.packetLossRatio = None
        else:
            self.packetLossRatio = (lost / (rxPackets + lost))

        interrupt_hist_elem = flow_el.find("flowInterruptionsHistogram")
        if interrupt_hist_elem is None:
            self.flowInterruptionsHistogram = None
        else:
            self.flowInterruptionsHistogram = Histogram(interrupt_hist_elem)


## ProbeFlowStats
class ProbeFlowStats(object):
    ## class variables
    ## @var probeId
    #  probe ID
    ## @var packets
    #  network packets
    ## @var bytes
    #  bytes
    ## @var delayFromFirstProbe
    #  delay from first probe
    ## @var __slots__
    #  class variable list
    __slots__ = ['probeId', 'packets', 'bytes', 'delayFromFirstProbe']


## Simulation
class Simulation(object):
    ## class variables
    ## @var flows
    #  list of flows
    def __init__(self, simulation_el):
        ''' The initializer.
        @param self The object pointer.
        @param simulation_el The element.
        '''
        self.flows = []
        FlowClassifier_el, = simulation_el.findall("Ipv4FlowClassifier")
        flow_map = {}
        for flow_el in simulation_el.findall("FlowStats/Flow"):
            flow = Flow(flow_el)
            flow_map[flow.flowId] = flow
            self.flows.append(flow)
        for flow_cls in FlowClassifier_el.findall("Flow"):
            flowId = int(flow_cls.get('flowId'))
            flow_map[flowId].fiveTuple = FiveTuple(flow_cls)

        for probe_elem in simulation_el.findall("FlowProbes/FlowProbe"):
            probeId = int(probe_elem.get('index'))
            for stats in probe_elem.findall("FlowStats"):
                flowId = int(stats.get('flowId'))
                s = ProbeFlowStats()
                s.packets = int(stats.get('packets'))
                s.bytes = int(stats.get('bytes'))
                s.probeId = probeId
                if s.packets > 0:
                    s.delayFromFirstProbe = parse_time_ns(stats.get('delayFromFirstProbeSum')) / float(s.packets)
                else:
                    s.delayFromFirstProbe = 0
                flow_map[flowId].probe_stats_unsorted.append(s)


def ProcessXMLFile(filename):
    file_obj = open(filename)
    # print ("Reading XML file ",filename)

    sys.stdout.flush()
    level = 0
    sim_list = []
    for event, elem in ElementTree.iterparse(file_obj, events=("start", "end")):
        if event == "start":
            level += 1
        if event == "end":
            level -= 1
            if level == 0 and elem.tag == 'FlowMonitor':
                sim = Simulation(elem)
                sim_list.append(sim)
                elem.clear()  # won't need this any more
                # sys.stdout.write(".")
                sys.stdout.flush()
    # print (" done.")

    th = []
    rth = []
    wth = []

    for sim in sim_list:
        sum = 0
        # th=[]
        # print()
        for flow in sim.flows:
            t = flow.fiveTuple
            proto = {6: 'TCP', 17: 'UDP'}[t.protocol]
            if flow.txBitrate is None:
                print("\tTX bitrate: None")
            else:
                th.append(flow.txBitrate)
                if t.destinationAddress == '1.161':
                    wth.append(flow.txBitrate)
                else:
                    rth.append(flow.txBitrate)

    return th, rth, wth


def checkSize(filename):
    file_obj = open(filename)
    # print ("Reading XML file ",filename)

    sys.stdout.flush()
    level = 0
    sim_list = []
    for event, elem in ElementTree.iterparse(file_obj, events=("start", "end")):
        if event == "start":
            level += 1
        if event == "end":
            level -= 1
            if level == 0 and elem.tag == 'FlowMonitor':
                sim = Simulation(elem)
                sim_list.append(sim)
                elem.clear()  # won't need this any more
                # sys.stdout.write(".")
                sys.stdout.flush()
    # print (" done.")

    size = []
    rsize = []
    wsize = []

    for sim in sim_list:
        sum = 0
        # th=[]
        # print()
        for flow in sim.flows:
            t = flow.fiveTuple
            proto = {6: 'TCP', 17: 'UDP'}[t.protocol]
            if flow.rxPackets is None:
                print("\tTX bitrate: None")
            else:
                size.append(flow.rxPackets)
                if t.destinationAddress == '1.161':
                    wsize.append(flow.rxPackets)
                else:
                    rsize.append(flow.rxPackets)

    return size, rsize, wsize


def printThroughputs(th):
    print(len(th), np.mean(th), np.median(th), np.percentile(th, 10))


def Compare2(th, th1):
    print(len(th), np.mean(th), np.median(th), np.percentile(th, 10))  # mode(th), th.count(mode(th)))
    print(len(th1), np.mean(th1), np.median(th1), np.percentile(th1, 10))  # mode(th1), th1.count(mode(th1)))
    # bin_size=5000
    # mx=int(max(max(th),max(th1)))
    # mn=int(min(min(th),min(th1)))
    # bin_num=ceil((mx-mn) / bin_size)
    # ecdf=ECDF(th)
    # ecdf1=ECDF(th1)
    # plt.plot(ecdf.x, ecdf.y,'r',ecdf1.x, ecdf1.y,'b')
    # plt.show()


def DrawCDF(th1, bin_size):
    f, axs = plt.subplots(3, 1, sharex=True)
    for x, th in enumerate(th1):
        print(len(th), np.mean(th), mode(th), th.count(mode(th)))
        mx = int(max(th))
        mn = int(min(th))
        bin_num = ceil((mx - mn) / bin_size)
        ecdf = ECDF(th)
        axs[x].plot(ecdf.x, ecdf.y)

    plt.xlim(0, 100)
    plt.show()


def main(argv):
    s, rs, ws = checkSize(argv[1])
    # DrawCDF([s,rs,ws],1)

    th, rth, wth = ProcessXMLFile(argv[1])
    # th1,rth1,wth1 = ProcessXMLFile(argv[2])

    # Compare2(th,th1)
    printThroughputs(th)
    # Compare2(rth,rth1)
    # Compare2(wth,wth1)
    # print ("\tTX bitrate: %.2f kbit/s" % (flow.txBitrate*1e-3,))
    # if flow.rxBitrate is None:
    #    print ("\tRX bitrate: None")
    # else:
    #    print ("\tRX bitrate: %.2f kbit/s" % (flow.rxBitrate*1e-3,))
    # if flow.delayMean is None:
    #    print ("\tMean Delay: None")
    # else:
    #    print ("\tMean Delay: %.2f ms" % (flow.delayMean*1e3,))
    # if flow.packetLossRatio is None:
    #    print ("\tPacket Loss Ratio: None")
    # else:
    #    print ("\tPacket Loss Ratio: %.2f %%" % (flow.packetLossRatio*100))
    # sum=sum+flow.txBitrate*1e-3
    # print(sum/len(sim.flows))


if __name__ == '__main__':
    main(sys.argv)
