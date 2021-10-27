import errno
import os
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Union
from rich import print
from pyecharts import Bar, Line

NodeRates = namedtuple('NodeRates', 'times rates')


def file_exist_notEmpty_check(file : Path):
    if not file.exists():
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), file)
    if file.stat().st_size == 0:
        raise Exception(f'{file.name} is empty')


def echarts_add2line(line:Line, name :str, x: list[int], y:list[int])->None:
    line.add(name, x, y,
             is_datazoom_show=True,
             datazoom_type="slider",
             # mark_line=["average"],
             is_datazoom_extra_show=True,
             datazoom_extra_type="slider",
             mark_point=["max", "min"],
             is_more_utils=True,
             is_selected = True,
             grid_top= '30%',
             grid_bottom='30%',
             yaxis_name= 'Gbps',
             xaxis_name='us'
             )



def sending_rate_line_drawing(
        path: Union[Path, str],
        nodes: defaultdict(lambda: {'times': list[int], 'rates':list[int]}))\
        -> None:
    if isinstance(path, str): path = Path(path)
    html = path.parent / 'sending_rate.html'
    line = Line(
        'Sending Rates',
        width=1200,
        height=600,

    )
    i = 0
    for node, (times, rates) in nodes.items():
        echarts_add2line(line, str(node), times, rates)
        i += 1
    line.render(html)


def pause_bar(path, times, ps, pr, duration, title):
    times = [time // 100000 * 100 for time in times]
    bar = Bar(title,
              f'duration {duration // 1000} us',
              width=1200,
              height=600,
              )

    bar.add("PAUSE_S", times, ps,
            is_datazoom_show=True,
            datazoom_type="slider",
            mark_line=["average"],
            is_datazoom_extra_show=True,
            datazoom_extra_type="slider",
            mark_point=["max", "min"],
            is_more_utils=True,
            )
    bar.add("PAUSE_R", times, pr,
            is_datazoom_show=True,
            datazoom_type="slider",
            mark_line=["average"],
            is_datazoom_extra_show=True,
            datazoom_extra_type="slider",
            mark_point=["max", "min"],
            is_more_utils=True
            )
    bar.render(path)


def pause_log(log: Union[Path, str], range: tuple[int, int] = (280, 288), ) -> None:
    if isinstance(log, str): log = Path(log)
    file_exist_notEmpty_check(log)
    duration = 100000  # nano
    log_pause = log.parent / 'pause_log.txt'
    mss, pauses = [], []

    with open(log, 'r') as infile, open(log_pause, 'w') as out:
        for line in infile:
            words = line.strip().split(' ')
            if len(words) < 3: continue
            if words[2] == 'PAUSE_R':
                if range[0] > int(words[1]) or int(words[1]) > range[1]:
                    continue
            if words[2] == 'PAUSE_S' or words[2] == 'PAUSE_R':
                out.write(line)
                mss.append(int(words[0]))
                pauses.append(words[2])
    ps, pr = [0], [0]
    times = [mss[0], mss[0] + duration]

    for time, pause in zip(mss, pauses):
        if time > times[-1]:
            times.append(times[-1] + duration)
            ps.append(0)
            pr.append(0)
        if pause == 'PAUSE_S': ps[-1] += 1
        if pause == 'PAUSE_R': pr[-1] += 1

    ps_rates = [p * 10 * 1000 for p in ps]
    pr_rates = [p * 10 * 1000 for p in pr]
    ps_rate = sum(ps_rates) / len(ps_rates)
    pr_rate = sum(pr_rates) / len(pr_rates)

    title = f'spine: pause_r = {sum(pr)}; pause_s = {sum(ps)}\n' \
            f'avg spine pause_r rate: {int(pr_rate):,} per s\n' \
            f'avg total pause_s rate: {int(ps_rate):,} per s'
    pause_bar(log.parent / 'pause_bar.html',
              times[1:], ps, pr, duration, title)


def sending_rate_log_parser(log: Union[Path, str]):
    '''

    :param log:
    :return:
    .. _sending rate log:

    sending rate log
    ~~~~~~~~~~~~~~~~~~
    eg::

        log.txt:
            8941052 284 Queue 1030
            8941060 45 m_rate for every packet 8000000000bps

    >>> sending_rate_log_parser("log.txt")
    8941060 45 m_rate for every packet 8000000000bps
    '''

    if isinstance(log, str): log = Path(log)
    file_exist_notEmpty_check(log)

    sr_file = log.parent / 'sending_rate_log.txt'
    nodes = defaultdict(lambda: NodeRates([], []))

    with open(log, 'r') as infile, open(sr_file, 'w') as out:
        for line in infile:
            if 'every packet' in line:
                out.write(line)
                words = line.strip().split(' ')
                nodes[int(words[1])].times.append(int(words[0]) / 10 ** 3)
                nodes[int(words[1])].rates.append(int(words[-1][:-3]) / 10 ** 9)
    sending_rate_line_drawing(log, nodes)



if __name__ == '__main__':
    sending_rate_log_parser('log.txt')



