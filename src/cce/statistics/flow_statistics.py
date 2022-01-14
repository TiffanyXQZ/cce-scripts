from collections import defaultdict
from pathlib import Path
from typing import Union
import csv

from pyecharts import Bar


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

    res = [0]; cur = 1.0
    for row in data:
        if row[2] <= cur: res[-1] += 1
        else:
            cur += 1.0
            res.append(1)
    return res
def flow_count_draw_bar(path, flows: list, title = 'flow count', )->None:
    bar = Bar(title,
              "number of flows per ms",
              width=1200,
              height=600,
              )

    bar.add("flow counts", list(range(1, len(flows) + 1)), flows,
            is_datazoom_show=True,
            datazoom_type="slider",
            mark_line=["average"],
            is_datazoom_extra_show=True,
            datazoom_extra_type="slider",
            mark_point=["max", "min"],
            is_more_utils=True,
            )

    bar.render(path)

def pause_count(src: Union[str, Path], dst:Union[str, Path] = 'pause_log_count.csv'):
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
    if isinstance(src,str): src = Path(src)
    if isinstance(dst,str): dst = src.parent / dst

    res = defaultdict(lambda : [0, 0])
    with open(src, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        for line in reader:
            if not line: continue
            k = int(line[1])
            if line[2] == 'PAUSE_S': res[k][1] += 1
            else: res[k][0] += 1
    res = [[k] + v for k, v in res.items()]
    res.sort()
    with open(dst, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['node id', 'number of pause_s', 'number of pause_r'])
        for row in res:
            writer.writerow(row)


