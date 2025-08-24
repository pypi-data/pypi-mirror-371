from os                  import chdir, getcwd, name, rename, system, walk
from re                  import match, I
from papermill           import execute_notebook
from rpy2.robjects       import r
from stata_kernel.config import config as stata_config
from oct2py              import Oct2Py

# autorun function
def autorun(
    path_data=getcwd(), pattern='', *args, **kwargs
):
    """
    Expandable Statistical Data Utilities
    -------------------------------------
    
    Cross-platform batch runner for statistical and numerical files.
    
    Requirements:
    -------------
    - At least one of the following must be installed and accessible:
        • Jupyter Notebook (.ipynb)      — uses `papermill`
        • R (.R)                         — uses `rpy2.robjects`
        • Stata (.do)                    — requires `stata_kernel.config`
        • Julia (.jl)                    — `julia` must be in PATH
        • GAMS (.gms)                    — `gams` must be in PATH
        • AMPL (.run)                    — `ampl` must be in PATH
        • MATLAB / Octave (.m)           — uses `matlab.engine` or `Oct2Py`
    
    Function:
    ---------
    autorun(path_data='...', pattern='...', *args, **kwargs)
    
        Automatically runs matching statistical scripts in the given directory.
        Generates .log files with outputs for each executed file.
    
        Parameters:
            path_data : str
                    Path to the directory with input files. Defaults to current
                    directory.
            pattern : str
                    Regex pattern to match file names (optional).
    
        Supported extensions and execution method:
            .ipynb — Jupyter notebook
            .R     — R script
            .do    — Stata batch mode
            .jl    — Julia script
            .gms   — GAMS script
            .run   — AMPL script
            .m     — MATLAB (via matlab.engine) or Octave (via oct2py)
    """
    stata  = stata_config.get('stata_path')
    julia  = 'julia'                                   # must be in PATH        
    gams   = 'gams'
    ampl   = 'ampl'
    octave = Oct2Py()

    chdir(path_data)                                   # cd to DATA/<folder>    
    for root, dirs, files in walk('.'):
        for file in files:
            # 1. Jupyter
            if match(pattern, file, I) and file.endswith('.ipynb'):
                execute_notebook(file, file, kwargs)
            # 2. R
            if match(pattern, file, I) and file.endswith('.R'):
                with open(file + '.log', 'w') as f:
                    f.write(str(r.source(file)))
            # 3. Stata BE/SE/MP
            if match(pattern, file, I) and file.endswith('.do'):
                system(stata + (' /' if name == 'nt' else ' -') + 'bq ' + file)
                rename(file.replace('.do', '.log'), file + '.log')
            # 4. Julia
            if match(pattern, file, I) and file.endswith('.jl'):
                system(julia + ' ' + file + ' >' + file + '.log 2>&1')
            # 5. GAMS
            if match(pattern, file, I) and file.endswith('.gms'):
                system(gams + ' ' + file + ' >' + file + '.log 2>&1')
            # 6. AMPL
            if match(pattern, file, I) and file.endswith('.run'):
                system(ampl + ' ' + file + ' >' + file + '.log 2>&1')
            # 7. Matlab/Octave
            if match(pattern, file, I) and file.endswith('.m'):
                try:
                    import matlab.engine
                    M = matlab.engine.start_matlab()
                    M.addpath(path_data, nargout=0)
                    result = M.eval(file.replace('.m', ''), nargout=1)
                    with open(file + '.log', 'w') as f:
                        f.write(str(result))
                    M.quit()
                except ImportError:
                    # Fall back to Octave
                    octave = Oct2Py()
                    with open(file + '.log', 'w') as f:
                        f.write(str(octave.eval(file.replace('.m', '()'))))
        break
