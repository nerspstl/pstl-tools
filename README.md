# pstl-tools
Python scripts for making working with UMICH NERS PSTL Lab Equipment much easier

## Tested Python Versions
- v3.10

## Requried Packages
- pyvisa
- pyserial
- numpy

## Subpackages
### Install
#### Via Python virtutal enviroment (venv)
1. Ensure python is installed
2. Run in command line

```
python -m venv <path/to/directory/to/store/venvs/your-venv>
```

Replace python with the python version you want to use i.e. ```python3.10```

3. Now activate your python venv

For Linux or Mac

```
<path/to/directory/to/store/venvs>/bin/python
```

For Windows

```
<path/to/directory/to/store/venvs>/Scripts/activate.bat
```

4. Run pip install

```
python -m pip install pstl-tools
```

--or--

```
pip install pstl-tools
```

5. Must have one of the following

- VISA Library from LABVIEW or alternative

- Install pyvisa-py and other dependences (open-source version of the previous)

[For more help vith python venv](https://docs.python.org/3/library/venv.html)
### GUI Langmuir Example
Have a .CSV file comma delimlated with oneline of headers.

Run the following once python package is installed via pip install

```
gui_langmuir <-additional flags>
```

optional flags are
  - -f, --fname "path/to/filename ie dir/out.csv" default is lang_data.csv 
  - -s,--sname "path/to/saveimages.png" default is test_gui.png

i.e.
```
gui_langmuir -f my_csv.csv -s my_pic.png
```

this runs a single Langmuir probe anaylsis and saves graphs when save button is hit

future updates will have buttons to change the analysis methods
