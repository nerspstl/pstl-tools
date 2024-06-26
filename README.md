# pstl-tools
Python scripts for making working with UMICH NERS PSTL Lab Equipment much easier

## Current Version
v2024.06.9

## Python Version
- >v3.11

## Requried Packages
- pyvisa (with VISA library aviable or pyvisa-py)
- numpy
- scipy
- pandas
- matplotlib
## Optional Packages
### pyvisa-py
- pyvisa-py
### dev
- pip-tools
- psutil
- zeroconf
### other
- pyserial
- alicat

## Subpackages
### Install
#### Via Python virtutal enviroment (venv)
1. Ensure python is installed
2. Run in command line

For Linux or Mac

```
python -m venv <path/to/directory/to/store/venvs/your-venv>
```

For Windows

```
python -m venv <path\to\directory\to\store\venvs\your-venv>
```

Replace python with the python version you want to use i.e. ```python3.11```

3. Now activate your python venv

For Linux or Mac

```
source <path/to/directory/to/store/venvs>/bin/activate
```

For Windows

```
<path\to\directory\to\store\venvs>\Scripts\activate.bat
```

4. Run pip install (If you have a VISA library installed, if not skip to step 5)

```
pip install pstl-tools
```

--or--

```
python -m pip install pstl-tools
```


5. Must have one of the following

- VISA Library from NI-LABVIEW or alternative

- Install pyvisa-py and other dependences (open-source version of the previous)

If no visa library (from NI-LABVIEW or Keysight etc), you may see an error saying:

```
ValueError: Could not locate a VISA implementation. Install either the IVI binary or pyvisa-py.
```

then, run the following

```
pip install pyvisa-py
```

[For more help with python venv](https://docs.python.org/3/library/venv.html)

### GUI Langmuir Example
Have a .CSV file comma delimlated with one-line for the headers.

Run the following once python package is installed via pip install

```
gui_langmuir <-additional flags> 
```

some optional flags are
  - -S, --settings_file "path/to/settings_file.json"

i.e.
```
gui_langmuir -S settings_gui_langmuir.json
```

this runs a single Langmuir probe anaylsis and saves graphs when save button is hit.

A template hardcoded settings file can be found at 
https://github.com/umich-pstl/pstl-tools/blob/main/tests/gui_langmuir/settings/settings_gui_langmuir-hardcode_template.json

A buidling template is like 
https://github.com/umich-pstl/pstl-tools/blob/main/tests/gui_langmuir/settings/settings_gui_langmuir-02.json
can also be used to in an automated script to quickly swap out probe JSON files.

In this JSON file, paths to the following are requried:
- solver.data.BUILD.file = <path\to\data\file.csv>
- solver.data.BUILD.negative = bool (false by default)
The kwargs have delimiter is set to "," but can be "\t" for tab-delimited. If there is a header set header=0 if not, null. If there are extra rows above the header set skiprows=number of these rows.

The plasma settings need to also be defined under
- solver.plasma.BUILD (either neutral_gas = xenon, krypton, neon or m_i needs to be defined)

The probe dimensions need to be defined as well under 
- solver.probe.BUILD.diameter = # (in meters)
- solver.probe.BUILD.length = # (in meters, leave as zero for planar)
- sovler.probe.BUILD.shape = (spherical, cylindrical, planar)

Optional definitions inclued
- preprocess = true (to remove noisy data points, default is true but maybe changed in the future) 
- name = "NAME-TO-DISPLAY-ON-SOLVER-GUI"
- canvas_kwargs.saveas = "BASENAME-TO-SAVE-PLOT-AS.png"
- cavas_kwargs.width(or height) = size of gui plots
- panal_kwargs.displays_kwargs.fname = "NAME-TO-SAVE-RESULTS.csv"


future updates will have additional buttons to change the analysis methods

Examples of the GUI Langmuir can be found in the same locations as the template.
Known issue in 
`settings_langmuir_solver-01.json`
using the negative index for fits.

## Acknowledgements
If you use this package for analysis, please acknowledge this package and version used.