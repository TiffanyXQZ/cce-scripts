
import typer

def main(path:str, pfc:int = 100, kmax:int =100, qcn:bool = False ):
    print(path, pfc, kmax, qcn)
    pass

if __name__ == '__main__':
    typer.run(main)
