import typer, sys, getpass, subprocess, pathlib, os,shutil
from cce.bo.bo_parser import ProcessXMLFile
from cce.parser.queue_parser import count_spine_pause_r
from cce.config.setting import *
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

    work_dir = pathlib.Path(path)
    os.chdir(work_dir)
    result_folder = work_dir / f'pfc_{pfc}_kmax{kmax}_qcn_{int(qcn)}'
    result_folder.mkdir(exist_ok=True)
    s = set_config({'PFC': str(pfc),
                    'KMAX': str(kmax),
                    'ENABLE_QCN': str(int(qcn)),
                    'TRACE_OUTPUT_FILE':str(result_folder / 'mix.tr')
                    })
    cur_config_txt = result_folder / 'config.txt'
    with open(cur_config_txt, 'w') as f: f.write(s)
    cur_log_txt = result_folder / 'log.txt'

    with open(cur_log_txt, 'w') as f:
        subprocess.run(
            ['./main.exe', cur_config_txt],
            stdout=f,
            stderr=f,
            text=True,
        )


    #          flow.txt     mix.tr
    files = ['FLOW_FILE']
    for f in files: shutil.copy(CONFIG_TXT[f], result_folder)
    shutil.copy(f'flow_monitor.xml', result_folder )



@app.command()
def hello(name: str = 'world'):
    typer.echo(f"Hello {name}")


@app.command()
def kmax_sensitiviy_run(path: str = typer.Argument(..., help="The path to run.bat")):
    work_dir = pathlib.Path(path)
    os.chdir(work_dir)
    pfc = 100
    qcn = 1


    for kmax in range(20, 100, 20):
        for i in range(1, 4):

            result_folder = work_dir / f'pfc_{pfc}_kmax{kmax}_qcn_{int(qcn)}_test{i}'
            result_folder.mkdir(exist_ok=True)
            s = set_config({'PFC': str(pfc),
                            'KMAX': str(kmax),
                            'ENABLE_QCN': str(int(qcn)),
                            'TRACE_OUTPUT_FILE': str(result_folder / 'mix.tr')
                            })
            cur_config_txt = result_folder / 'config.txt'
            with open(cur_config_txt, 'w') as f:
                f.write(s)
            cur_log_txt = result_folder / 'log.txt'

            with open(cur_log_txt, 'w') as f:
                subprocess.run(
                    ['./main.exe', cur_config_txt],
                    stdout=f,
                    stderr=f,
                    text=True,
                )

            #          flow.txt     mix.tr
            files = ['FLOW_FILE']
            for f in files: shutil.copy(CONFIG_TXT[f], result_folder)
            shutil.copy(f'flow_monitor.xml', result_folder)






@app.command()
def pfc_sensitiviy_run(path: str = typer.Argument(..., help="The path to run.bat")):
    work_dir = pathlib.Path(path)
    os.chdir(work_dir)
    print(pathlib.Path().resolve())
    kmax = 100
    qcn = 1
    for pfc in range(50, 300, 50):
        for i in range(1, 4):
            result_folder = work_dir / f'pfc_{pfc}_kmax{kmax}_qcn_{int(qcn)}_test{i}'
            result_folder.mkdir(exist_ok=True)
            s = set_config({'PFC': str(pfc),
                            'KMAX': str(kmax),
                            'ENABLE_QCN': str(int(qcn)),
                            'TRACE_OUTPUT_FILE': str(result_folder / 'mix.tr')
                            })
            cur_config_txt = result_folder / 'config.txt'
            with open(cur_config_txt, 'w') as f:
                f.write(s)
            cur_log_txt = result_folder / 'log.txt'

            with open(cur_log_txt, 'w') as f:
                subprocess.run(
                    ['./main.exe', cur_config_txt],
                    stdout=f,
                    stderr=f,
                    text=True,
                )

            #          flow.txt     mix.tr
            files = ['FLOW_FILE']
            for f in files: shutil.copy(CONFIG_TXT[f], result_folder)
            shutil.copy(f'flow_monitor.xml', result_folder)


@app.command()
def flow_moniter_parser(path: str = typer.Argument(..., help="The path to test result folder and the script folder")):
    script = 'flowmon-parse-results.py'
    work_dir = pathlib.PureWindowsPath(path)
    os.chdir(path)
    print(pathlib.Path().resolve())

    # i (th, rth, wth) = ProcessXMLFile(argv[1])
    column = ["Test1", "flow#", "Mean Tht", "Median Tht", "10th Tht",
              "Total PAUSE_S", "SPINE PAUSE_R", "Test2", "flow#",
              "Mean Tht", "Median Tht", "10th Tht", "Total PAUSE_S",
              "SPINE PAUSE_R", "Test3", "flow#", "Mean Tht", "Median Tht",
              "10th Tht", "Total PAUSE_S", "SPINE PAUSE_R"]
    aves = ["Avg Mean Tht (Gbps)",
            "Avg Median Tht(Gbps)", "Avg 10th Tht(Gbps)", "Avg Total PAUSE_S", "Avg SPINE PAUSE_R"]

    folder_names = set()
    for folder in pathlib.Path('.').iterdir():
        if folder.is_dir() and folder != pathlib.Path('mix'):
            folder_names.add(folder.name[:-5])
    print(folder_names)

    import numpy as np
    import pandas as pd

    hs = ['th', 'rth', 'wth']
    dfs = []
    for i in range(3):
        # j (test1, test2, test3)
        data = []
        for folder in folder_names:
            row = []
            for j in range(1, 4):
                test = f'{folder}test{j}'
                # print(test)
                h = ProcessXMLFile(f'{test}/flow_monitor.xml')[i]
                with open(f'{test}/pause.txt', 'w') as f:
                    pause1, pause2 = count_spine_pause_r(f'{test}/log.txt')

                row += [test, len(h), np.mean(h), np.median(h), np.percentile(h, 10), pause1, pause2]
                # print(row)
            print('hello')
            data += [row]
        df = pd.DataFrame(data, columns=column)
        dfs.append(df)

    # with open( 'dfs.pickle', 'w') as f:
    #     pickle.dump(dfs, f)
    with pd.ExcelWriter('output.xlsx') as writer:
        for i, df in enumerate(dfs):
            df.to_excel(writer, sheet_name=f'{hs[i]}')

        # command = f'python {script} {folder}/flow_monitor.xml'
        # print(command)
        # with open(f'{folder}/throughput.txt', 'w') as f:
        #     print('hello')
        #     subprocess.run(
        #         ['C:/Users/xzhan/Desktop/cce-scripts/venv/Scripts/python.exe', script, f'{folder}/flow_monitor.xml'],
        #         stdout = f,
        #         text=True
        #     )

        # with open(f'{folder}/pause.txt', 'w') as f:
        #     res = count_spine_pause_r(f'{folder}/log')
        #     res = [str(i) for i in res]
        #     f.write(','.join(res))
    pass


if __name__ == '__main__':
    app()
