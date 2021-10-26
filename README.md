# cce-scripts
Congest Control Experiemnt Scripts (Network Lab UMB)

[Doc Page](https://tiffanyxqz.github.io/cce-scripts/)


 ## python version >=3.9 
Built-in type hints used. Lower version does not support this

## Run within editable mode
1. git pull this repo
2. setup an env with python>=3.9
3. activate the venv ()
4. pip install -r requirements.txt
5. pip install -e .
6. cce --help (to see all running options)
    eg: 
    ```console
    cce kmax-sensitiviy-run .
    ``` 
    this command runs kmax-sensitivity function in autorun.py with arguments of current folder ```. ```
    once you activated the venv, the cce command is within the ```PATH```
    
