import pathlib
from typing import Union


def count_spine_pause_r(
        queue: Union[str, pathlib.Path],
        range:tuple[int, int] = (280, 288),
        key: str = 'PAUSE_R') ->tuple[int, int]:
    '''

    :param queue: file path for queue
    :param range: spine level nodes
    :return: number of total pause_s; number of pause_r received by spine level nodes


    .. _target to count spine pause:

    count spine pause
    ~~~~~~~~~~~~~~~~~~
    eg::

        queue.txt:
            31116302 277 PAUSE_R
            31115502 264 PAUSE_S 53560

    >>> count_spine_pause_r("queue.txt")
    (1, 1)
    '''
    c1 = c2 = 0
    with open(queue, 'r') as f:
        for line in f:
            words = line.strip().split(' ')
            if len(words) == 4 and words[2] == 'PAUSE_S': c1 += 1
            if len(words) == 3 and words[2] == key:
                if range[0] <= int(words[1]) < range[1]:  c2 += 1
    return c1, c2

if __name__ == '__main__':
    import sys, getpass
    print(sys.platform, getpass.getuser())
    if getpass.getuser() == 'xzhan':
        path = r'C:\Users\xzhan\Desktop\CongestionControl\ssd_work_space\test\QCN\kmax50PFC50\Tencent1125-1W_24us_10_to_1_net-ssd\1\queue.txt'
        path = pathlib.PureWindowsPath(path)
        print(count_spine_pause_r(path))