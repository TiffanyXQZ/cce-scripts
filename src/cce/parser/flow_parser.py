import collections
import xml.etree.ElementTree as ET
from xml.etree import ElementTree

from rich import print

# from pyecharts import options as opts
# from pyecharts.charts import Tree


def string2float(s: str) -> float:
    '''

    :param s:
    possible format:
     '+0.0ns'
     '2056'
    :return:
    '''
    if not s[0].isnumeric():
        return float(s[1:-2])
    else:
        return float(s)


class ProbeFlowStats:
    def __init__(self, fs: ET.Element, id:int):
        '''

        :param fs:
        {
        'name': 'FlowStats',
        'count': 1000,
        'attribute': {
            'flowId': '1',
            'packets': '2',
            'bytes': '2056',
            'delayFromFirstProbeSum': '+0.0ns'
        },
        :param id: proble index
        '''
        for k, v in fs.attrib:
            fv = string2float(v)
            fv = int(fv) if fv.is_integer() else fv
            setattr(self, k, fv)
        self.probleId = id
        self.delayFromFirstProbe = self.delayFromFirstProbeSum / self.packets
        if self.packets > 0:
            self.delayFromFirstProbe = self.delayFromFirstProbeSum / self.packets
        else:
            self.delayFromFirstProbe = 0


class FlowInterruptionHistogram:
    def __init__(self, fihs: list[ET.Element]):
        '''

        :param fih:
        {
            'name': 'flowInterruptionsHistogram',
            'count': 1,
            'attribute': {'nBins': '0'},
            'children': []
        }
        '''
        self.nBins = [int(fih.get('nBins')) for fih in fihs]


class FlowStatsFlow:
    def __init__(self, flow_elem: ET.Element):
        '''

        :param flow_elem:
        {
            'name': 'Flow',
            'attribute': {
            'flowId': '1',
            'timeFirstTxPacket': '+0.0ns',
            'timeFirstRxPacket': '+8472.0ns',
            'timeLastTxPacket': '+135.0ns',
            'timeLastRxPacket': '+11768.0ns',
            'delaySum': '+20105.0ns',
            'jitterSum': '+3161.0ns',
            'lastDelay': '+11633.0ns',
            'txBytes': '2056',
            'rxBytes': '2056',
            'txPackets': '2',
            'rxPackets': '2',
            'lostPackets': '0',
            'timesForwarded': '10'
            }
        }
        '''
        # print(flow_elem.attrib)
        for k, v in flow_elem.attrib.items():
            fv = string2float(v)
            fv = int(fv) if fv.is_integer() else fv
            setattr(self, k, fv)
        self.rx_duration = self.timeLastRxPacket - self.timeFirstTxPacket   # flow completion time
        self.tx_duration = self.timeLastTxPacket - self.timeLastRxPacket
        if self.rxPackets:
            self.hopCount = self.timesForwarded / self.rxPackets + 1
            self.delayMean = self.delaySum / self.rxPackets
            self.packetSizeMean = self.rxBytes / self.rxPackets
            self.packetLossRatio = (self.lostPackets / (self.rxPackets + self.lostPackets))
        else:
            self.hopCount = -1000
            self.delayMean = None
            self.packetSizeMean = None
            self.packetLossRatio = None

        if self.rx_duration > 0:
            self.rxBitrate = self.rxBytes * 8 / self.rx_duration
        else:
            self.rxBitrate = None

        if self.tx_duration > 0:
            self.txBitrate = self.txBytes * 8 / self.tx_duration
        else:
            self.txBitrate = None
        interrupt_hist_elem = flow_elem.find("flowInterruptionsHistogram")
        if interrupt_hist_elem is None:
            self.flowInterruptionsHistogram = None
        else:
            FlowInterruptionHistogram(interrupt_hist_elem)
    # def __str__(self):


# class FlowSizeInfo(FlowStatsFlow):
#     def __int__(self):
#         super(FlowSizeInfo, self).__int__()
#         self.fct = self.




class Ipv4FlowClassifierFlow:
    def __init__(self, iFlow: ET.Element):
        '''

        :param iFlow:
        {
        'name': 'Flow',
        'count': 10000,
        'attribute': {
            'flowId': '1',
            'sourceAddress': '1.1',
            'destinationAddress': '1.161',
            'protocol': '17',
            'sourcePort': '49153',
            'destinationPort': '9199'
        },
        '''
        self.sourceAddress = iFlow.get('sourceAddress')
        self.destinationAddress = iFlow.get('destinationAddress')
        self.sourcePort = int(iFlow.get('sourcePort'))
        self.destinationPort = int(iFlow.get('destinationPort'))
        self.protocol = int(iFlow.get('protocol'))


def flowstats_flows(root: ET.Element) -> dict[int, FlowStatsFlow]:
    res = {}
    for flow_ele in root.findall('FlowStats/Flow'):
        # print(flow_ele.attrib)
        flow = FlowStatsFlow(flow_ele)
        res[flow.flowId] = flow
    return res


def ipv4FlowClassifier_flows(root: ET.Element) -> dict[int, Ipv4FlowClassifierFlow]:
    res = {}
    for flow_ele in root.findall('Ipv4FlowClassifierFlow/Flow'):
        flow = Ipv4FlowClassifierFlow(flow_ele)
        res[flow.flowId] = flow
    return res


def flowprobes_flowprobe_flowstats(root: ET.Element)->dict[int, Ipv4FlowClassifierFlow]:
    res = {}
    for probe_ele in root.findall('FlowProbes/FlowProbe'):
        proble_index = int(probe_ele.get('index'))
        for stats in probe_ele.findall('FlowStats'):
            pstats = ProbeFlowStats(stats, proble_index)
            res[pstats.flowId] = pstats
    return res


def txBitrate_IP(xml:str, ip:str)->tuple[list,list, list]:
    '''
    return txBitrate ratio for a given ip
    th: all txBitrate
    rth: all txBitrate for the ip
    wth: all that not for the ip
    :param xml: flow_monitor.xml
    :param ip: ip address
    :return: (th, rth, wth)
    '''
    root = ET.parse(xml).getroot()
    flowstats = flowstats_flows(root)
    flows_class = ipv4FlowClassifier_flows(root)
    th, rth, wth = [],[],[]
    for id in flowstats.keys():
        th.append(flowstats[id].txBitrate)
        if flows_class[id].destinationAddress == ip: wth.append(th[-1])
        else: rth.append(th[-1])
    return th, rth, wth
# tree = ET.parse('../../../data/flow_monitor.xml')
# root = tree.getroot()
# data = {}


# def bfs(root):
#     q = collections.deque()
#     res = {'name':root.tag, 'children':[]}
#     q.append((root,res))
#
#     while q:
#         node, cur = q.popleft()
#         print(node, cur)
#         children = set()
#         print(cur)
#         for child in node: children.add((child.tag,child))
#         for tag, child in children:
#             print(cur)
#             cur['children'].append({'name': tag, 'children':[]})
#             q.append((tag, child))
#
#     return [res]
#
# print(bfs(root))

def tree_data(l):
    if len(l) == 0: return None
    mid = len(l) // 2
    children = []
    left, right = tree_data(l[0:mid]), tree_data(l[mid + 1:])
    if left: children.append(left)
    if right: children.append(right)

    return {'name': l[mid], 'children': children}


# print(tree_data([1,2,3,4,5]))


# tree_charts([tree_data([1, 2, 3, 4, 5, 6, 7])])

# tree = ET.parse('../../../data/flow_monitor.xml')
# root = tree.getroot()


def xml_tag_tree(root_xml: ElementTree) -> dict:
    '''

    :param root_xml: xml elementTree
    :return: root_tag: {'name': name, 'count':count, 'children':[]}
    '''
    root_tag, q = {'name': root_xml.tag, 'count': 1}, collections.deque()
    q.append((root_tag, root_xml))
    while q:
        node_tag, node_xml = q.popleft()
        # build children for current node_tag while a dict then covert it to list
        children = {}
        for child_xml in node_xml:
            if child_xml.tag not in children:
                child_tag = {
                    'name': child_xml.tag,
                    'count': 1,
                    'attribute': child_xml.attrib,
                    'children': []
                }
                q.append((child_tag, child_xml))
                children[child_xml.tag] = child_tag
            else:
                children[child_xml.tag]['count'] += 1
        node_tag['children'] = list(children.values())
    return root_tag


# tag_tree = xml_tag_tree(root)
# print(tag_tree)
# tree_charts([tag_tree])

if __name__ == '__main__':
    tree = ET.parse('../../../data/flow_monitor.xml')
    root = tree.getroot()
    fs = flowstats_flows(root)
    print(len(fs))
    print(fs[1].__dir__())
    print(fs[1].rx_duration)
    print(fs[1].timeLastRxPacket)
