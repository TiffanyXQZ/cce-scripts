import math
from collections import defaultdict
from pathlib import Path
from typing import Union
import csv

from pyecharts import Bar
import xml.etree.ElementTree as ET

from cce.parser.flow_parser import FlowStatsFlow, Ipv4FlowClassifierFlow


def flow_count(data: Union[Path, str, list]) -> list[int]:
    '''

    #csv schema
    #flowID   flow_size   timeFirstTxPacket timeLastRxPacket fct

    return the counts of flow in each 1 ms of timeFirstTxPacket

    :param csv:
    :return:
    '''

    if not isinstance(data, list):
        data_csv = []
        with open(data, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                row[0] = int(row[0])
                row[1] = int(row[1])
                row[2] = float(row[2])
                row[3] = float(row[3])
                row[4] = float(row[3])
                data_csv.append(row)
        data = data_csv

    res = [0];
    cur = 1.0
    for row in data:
        if row[2] <= cur:
            res[-1] += 1
        else:
            cur += 1.0
            res.append(1)
    return res


def byte_count_draw_bar(path, flows: list, title='byte count', ) -> None:
    '''
    flow: Byte/ms

    :param path:
    :param flows:
    :param title:
    :return:
    '''
    bar = Bar(title,
              "Gbps",
              width=1200,
              height=600,
              )
    flows = [flow * 1000 * 8 / 2**30  for flow in flows]
    bar.add("byte counts", list(range(1, len(flows) + 1)), flows,
            is_datazoom_show=True,
            datazoom_type="slider",
            mark_line=["average"],
            is_datazoom_extra_show=True,
            datazoom_extra_type="slider",
            mark_point=["max", "min"],
            is_more_utils=True,
            )

    bar.render(path)


def pause_count_all(src: Union[str, Path] = 'log.txt', dst: Union[str, Path] = 'pause_all_count.csv'):
    '''
    #input: name log.txt

    #time_stamp, node id, PAUSE TYPE(S | R),
    eg:
        1386615 264 PAUSE_S 104030


    # persist
    name: pause_all_count.txt
    schema:
        node id, number of pause_s, number of pause_r

    :param src:
    :param dst:
    :return:
    '''
    if isinstance(src, str): src = Path(src)
    if isinstance(dst, str): dst = src.parent / dst

    res = defaultdict(lambda: [0, 0])
    with open(src, 'r') as f:

        for line in f.readlines():
            line = line.strip().split(' ')
            if len(line) < 3 or \
                    (line[2] != 'PAUSE_S' and line[2] != 'PAUSE_R'):
                continue
            k = int(line[1])
            if line[2] == 'PAUSE_S':
                res[k][0] += 1
            else:
                res[k][1] += 1
    res = [[k] + v for k, v in res.items()]
    res.sort()
    with open(dst, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['node id', 'number of pause_s', 'number of pause_r'])
        for row in res:
            writer.writerow(row)


def pause_count(src: Union[str, Path], dst: Union[str, Path] = 'pause_log_count.csv'):
    '''
    #input: name pause_log.txt
    #csv schema
    #time_stamp, node id, PAUSE TYPE(S | R),
    eg:
        1386615 264 PAUSE_S 104030


    # persist
    name: pause_log_count.txt
    schema:
        node id, number of pause_s, number of pause_r

    :param src:
    :param dst:
    :return:
    '''
    if isinstance(src, str): src = Path(src)
    if isinstance(dst, str): dst = src.parent / dst

    res = defaultdict(lambda: [0, 0])
    with open(src, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        for line in reader:
            if not line: continue
            k = int(line[1])
            if line[2] == 'PAUSE_S':
                res[k][0] += 1
            else:
                res[k][1] += 1
    res = [[k] + v for k, v in res.items()]
    res.sort()
    with open(dst, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['node id', 'number of pause_s', 'number of pause_r'])
        for row in res:
            writer.writerow(row)


def byte_count(data: Union[Path, str, list]) -> list[int]:
    '''

    #csv schema
    #flowID   flow_size txBytes  timeFirstTxPacket timeLastRxPacket fct

    window: 1 ms duration starting from 0

    window_counts = (timeFirstTxPacket timeLastRxPacket) within 0, 1, 2, 3, 4
    each_window_bytes  = txBytes / window_counts

    total_bytes_per_window = all flows's each_window_bytes within that window


    :param csv:
    :return:
    '''

    if not isinstance(data, list):
        data_csv = []
        with open(data, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                row[0] = int(row[0])
                row[1] = int(row[1])
                row[2] = int(row[2])
                row[3] = float(row[3])
                row[4] = float(row[4])
                row[5] = float(row[5])
                data_csv.append(row)
        data = data_csv

    # window_counts_per_flow = {}

    res = [0] * math.ceil(max(data, key=lambda x: x[4])[4])
    for row in data:
        flowID, size, bytes, time_tx, time_rx, fct = row
        a, b = math.floor(time_tx), math.ceil(time_rx)
        # window_counts_per_flow[flowID] = bytes / (b - a)
        for i in range(a, b): res[i] += bytes / (b - a)

    return res




def sd_startTime_flowtxt(src:str = 'flowtxt.csv') -> dict[str, list]:
    '''
    sourceAddress	destinationAddress	Priority	txPackets	flowStartTime	simulatorEndTime

    ['1.1', '1.161', '3', '92', '0.000089', '10.00009']

    second -> nano second
    :param src:
    :return: (sourceAddress, destinationAddress) : [flowStartTime]
    '''

    src = Path(src)
    ip_t1 = defaultdict(list)

    with open(src, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for (s, d, p, tx, st, et) in reader:
            ip_t1[(s, d)].append(float(st))
    return ip_t1

def flowstats_timeLastRxPacket(src : str =  'flow_monitor.xml'):
    '''


    flowid : (timeLastRxPacket, txBytes)
    :param src:
    :return:
    '''
    tree = ET.parse(src)
    root = tree.getroot()
    res = {}
    for flow_ele in root.findall('FlowStats/Flow'):
        # print(flow_ele.attrib)
        flow = FlowStatsFlow(flow_ele)
        res[flow.flowId] = (flow.timeLastRxPacket, flow.txBytes)
    return res

def flowIP_flowID(src : str =  'flow_monitor.xml'):

    tree = ET.parse(src)
    root = tree.getroot()
    ip_ids = defaultdict(list)
    id_ip = {}
    # print(root.findall('Ipv4FlowClassifier/Flow'))
    for flow_ele in root.findall('Ipv4FlowClassifier/Flow'):

        flow = Ipv4FlowClassifierFlow(flow_ele)
        ip = (flow.sourceAddress, flow.destinationAddress)
        ip_ids[ip].append(flow.flowId)
        id_ip[flow.flowId] = ip

    return ip_ids, id_ip










def newFCT(flow_monitor: str, flow_txt:str):
    '''

    id  ip1  ip2  t1  t2  txBytes, newFCT, th


    newFCT = t2 - t1
    th = txBytes * 8 / newFCT

    time : nano second

    :param flow_monitor:
    :param flow_txt:
    :return:
    '''

    ip_t1 = sd_startTime_flowtxt(flow_txt)
    ip_ids, id_ip = flowIP_flowID(flow_monitor)
    id_t1 = {}
    for ip, t1s in ip_t1.items():
        # print(t1s)
        # print(ip_ids[ip])
        # print(len(t1s), len(ip_ids[ip]))
        # raise errno
        for t1, id in zip(t1s, ip_ids[ip]):
            id_t1[id] = t1


    # print(sorted(id_t1.keys()))
    id_t2_tx = flowstats_timeLastRxPacket(flow_monitor)

    schema = ['flowid', 'ip1', 'ip2', 'flow_start_time',
              'flow_end_time', 'txBytes', 'newFCT', 'throughput',
              'mean throughout', 'median throughpu', '10th throughput']
    conversion_flow = 8 * 10**(-9) # byte to Gbit
    conversion_time = 1 / 10**9 # nano second -> second
    flow_monitor = Path(flow_monitor)
    fct_csv = flow_monitor.parent / 'newfct.csv'


    res = []; ths = []
    for id, ip in id_ip.items():
        ip1, ip2 = ip
        if id not in id_t1: continue
        t1 = id_t1[id]
        # print(t1)
        # print(id_t2_tx[id])
        t2, tx = id_t2_tx[id]
        t2 *= conversion_time

        fct = t2 - t1
        th = tx * conversion_flow / fct
        ths.append(th)

        row = [id, ip1, ip2, t1, t2, tx, fct, th]
        res.append(row)

    ths.sort()
    ave = sum(ths) / len(ths)
    i = len(ths) // 2
    mid = len(ths) // 2
    if len(ths) & 1:
        median = ths[mid]
    else:
        median = (ths[mid] + ths[mid - 1]) / 2



    tenth = ths[len(ths)// 10]

    addon = [str(ave), str(median), str(tenth)]



    with open(fct_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(schema)
        for row in res:
            writer.writerow([str(i) for i in row + addon])


def newFCT_statistics(newfct: str):
    '''
    newfct.csv
        schema = ['flowid', 'ip1', 'ip2', 'flow_start_time',
              'flow_end_time', 'txBytes', 'newFCT', 'throughput']

    to

        schema = ['flowid', 'ip1', 'ip2', 'flow_start_time',
              'flow_end_time', 'txBytes', 'newFCT', 'throughput',
              'mean throughout', 'median throughpu', '10th throughput']


    :param src:
    :return:
    '''

    schema = ['flowid', 'ip1', 'ip2', 'flow_start_time',
              'flow_end_time', 'txBytes', 'newFCT', 'throughput',
              'mean throughput', 'median throughput', '10th throughput']


    res = []
    ths = []
    with open(newfct, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            ths.append(float(row[-1]))
            res.append(row)

    ths.sort()
    ave = sum(ths) / len(ths)
    i = len(ths) // 2
    mid = len(ths) // 2
    if len(ths) & 1: median = ths[mid]
    else: median = (ths[mid] + ths[mid-1]) / 2

    tenth = ths[-10]

    addon = [str(ave), str(median), str(tenth)]

    with open(newfct, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(schema)
        for row in res: writer.writerow(row + addon)




if __name__ == '__main__':
    flow_txt = r'C:\Users\netwo\Desktop\tiffany\edited-tiffany-newAdjustRate_ns3-rdma\ns3-rdma-copy\windows\ns-3-dev\x64\Release\mix\flowtxt.csv'
    # print(sd_startTime_flowtxt(src))
    #

    flow_monitor = r'C:\Users\netwo\Desktop\tiffany\edited-tiffany-newAdjustRate_ns3-rdma\ns3-rdma-copy\windows\ns-3-dev\x64\Release\mix\TrackLowestRate\checkActiveFlow_timer50\pfc_100_kmax20_qcn_1_test1\flow_monitor.xml'

    newFCT(flow_monitor, flow_txt)

    # print(flowstats_timeLastRxPacket(src))
    # print(flowIP_flowID(src))

    # print(timeLastRXPackets_flowmonitor(src))


