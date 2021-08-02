import os
import pathlib
import subprocess

import typer,sys, getpass

from cce.parser.queue_parser import count_spine_pause_r

app = typer.Typer()


@app.command()
def run(path: str = typer.Argument(..., help="The path to main.exe"),
        pfc: int = typer.Option(100, help="p f c not kfc"),
        kmax: int = typer.Option(100, help="kmax not kmin"),
        qcn: bool = typer.Option(False, help="qcn or non-qcn"),
        ):
    '''

    :param path:
    :param pfc:
    :param kmax:
    :param qcn:
    :return:
    '''
    print(path, pfc, kmax, qcn)


@app.command()
def hello(name: str = 'world'):
    typer.echo(f"Hello {name}")
@app.command()
def flow_moniter_parser(path: str = typer.Argument(..., help="The path to test result folder and the script folder")):

    script = 'flowmon-parse-results.py'
    work_dir = pathlib.PureWindowsPath(path)
    os.chdir(path)
    print(pathlib.Path().resolve())


    for folder in pathlib.Path('.').iterdir():
        if folder.is_dir() and folder != pathlib.Path('mix'):
            command = f'python {script} {folder}/flow_monitor.xml'
            # print(command)
            # with open(f'{folder}/throughput.txt', 'w') as f:
            #     print('hello')
            #     subprocess.run(
            #         ['C:/Users/xzhan/Desktop/cce-scripts/venv/Scripts/python.exe', script, f'{folder}/flow_monitor.xml'],
            #         stdout = f,
            #         text=True
            #     )

            with open(f'{folder}/pause.txt', 'w') as f:
                res = count_spine_pause_r(f'{folder}/log')
                res = [str(i) for i in res]
                f.write(','.join(res))
    pass




if __name__ == '__main__':
    app()
