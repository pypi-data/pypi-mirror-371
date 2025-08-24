# DATAU - Batch Statistical Data Utilities

Cross-platform batch runner for statistical and numerical files.

## Installation

```bash
pip install pydatau
```

## Quick example
```python
from datau import autorun

autorun(path_data="my_project/data", pattern='master')
```

## Supported Extensions and Execution Method

| Extension | Language/Tool    | Method                      |
|-----------|------------------|-----------------------------|
| `.ipynb`  | Jupyter Notebook | `papermill`                 |
| `.R`      | R                | `rpy2.robjects`             |
| `.do`     | Stata            | Stata batch mode            |
| `.jl`     | Julia            | `julia` (must be in PATH)   |
| `.gms`    | GAMS             | `gams` (must be in PATH)    |
| `.run`    | AMPL             | `ampl` (must be in PATH)    |
| `.m`      | MATLAB / Octave  | `matlab.engine` or `Oct2Py` |

## User Reference

```python
autorun(path_data='...', pattern='...', *args, **kwargs)
```

Automatically runs matching statistical scripts in the given directory. Generates `.log` files with outputs for each executed file.

**Parameters:**  

`path_data` : *str*, default = *current working directory*  
Path to the directory with input files.

`pattern` : *str*, optional  
Regex pattern to match file names, such as *'master'*.
