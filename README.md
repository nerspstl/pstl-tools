# pstl-tools
Python scripts for making working with UMICH NERS PSTL Lab Equipment much easier

## Tested Python Versions
- v3.9.6

## Requried Packages
- pyvisa
- pyserial
- numpy

## Subpackages
### rs232
Baisis for interacting via usb-2-rs232 adapter (download driver for usb-2-rs232 adapater)

Be sure to know COM# port number (windows) or /dev/ttyS# (linux)

_main_pumpdown.py_

gets pressure date versus time and saves to a .csv (comma delimited) file

to run enter the following in the directory (folder) containing main_pumpdown.py

```
python main_pumpdown.py <-additional flags>
```

optional flags are
  - -f, --fname "path/to/filename ie dir/out.csv" default is test_out.csv 
  - -d,--delay "delay time between data collection" default is 1 secound
  - -p,--port "port number ie Windows 'COM5',Linux ttyS0" default is COM8
  - -s,--string "input command to run in loop" default is =RV for KJL Ion gauage controller

i.e.
```
python main_pumpdown.py -f my_csv.csv -p COM5
```

this runs main_pumpdown.py and saves data to my_csv.csv and communicates via COM5

future updates will have a defaults option that will make it easier to run for beginners 
