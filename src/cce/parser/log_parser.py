from pathlib import Path
from typing import Union
from rich import print
from pyecharts import Bar

from .queue_parser import count_spine_pause_r


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

    duration = 100000  # nano
    log_pause = log.parent / 'pause_log.txt'
    mss, pauses = [], []

    with open(log, 'r') as infile, open(log_pause, 'w') as out:
        for line in infile:
            line1 = line.strip().split(' ')
            if len(line1) < 3: continue
            if line1[2] == 'PAUSE_R':
                if range[0] > int(line1[1]) or int(line1[1]) > range[1]:
                    continue
            if line1[2] == 'PAUSE_S' or line1[2] == 'PAUSE_R':
                out.write(line)
                mss.append(int(line1[0]))
                pauses.append(line1[2])
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


if __name__ == '__main__':
    pause_log('log.txt')
