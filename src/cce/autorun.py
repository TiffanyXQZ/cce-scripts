import typer

app = typer.Typer()


@app.command()
def run(path: str = typer.Argument(..., help="The path to main.exe"),
        pfc: int = typer.Option(100, help="p f c not kfc"),
        kmax: int = typer.Option(100, help="kmax not kmin"),
        qcn: bool = typer.Option(False, help="qcn or non-qcn")):
    print(path, pfc, kmax, qcn)


@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")


if __name__ == '__main__':
    app()
