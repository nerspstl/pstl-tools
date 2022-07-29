#!/usr/bin/env python
import argparse

import rs232 as rs

# argparse
parser = argparse.ArgumentParser()
parser.add_argument("-D","--defaults",\
        help="imports defaults from defaults_daq.py"+\
        "overides anyother flag",action="store_true")
parser.add_argument("-f","--fname",\
        help="path/to/filename ie dir/out.csv",type=str)
parser.add_argument("-d","--delay",\
        help="delay time between data collection",type=float)
parser.add_argument("-H","--header",\
        help="header for csv file 1x2 list",nargs="+")
parser.add_argument("-p","--port",\
        help="port number ie Windows 'COM5',Linux ttyS0",type=str)
parser.add_argument("-cmd","--command",\
        help="input command to run in loop",type=str)
parser.add_argument("-ch","--channel",\
        help="input channel to run cmd on",type=int)
parser.add_argument("-c","--card",\
        help="input card number to run on",type=int)
parser.add_argument("-b","--baudrate",\
        help="input baudrate",type=int)
args = parser.parse_args()

if args.defaults:
    import defaults_daq as daq
    cnvrt = daq.convert
    fname = daq.fname
    delay = daq.delay
    header = daq.header
    port = daq.port
    cmd = daq.cmd
    channel = daq.channel
    card = daq.card
    baudrate = daq.baudrate
    test = daq.test
else:

    # convert
    cnvrt = False #dfault

    # channel
    if args.channel is None:
        ch = int(input('Please enter channel number (i.e. 1-30)>>'))
    else:
        ch = args.channel

    # card
    if args.card is None:
        card = str(input('Please enter card number (i.e. 1-3)>>'))
    else:
        card = args.card

    # set up loc to recieve command
    if ch < 10:
        ch = "0"+str(ch)
    else:
        ch = str(ch)
    loc = card+ch

    # port
    if args.port is None:
        port = str(input('Please enter port (i.e. windows: COM3;linux /dev/tty0)>>'))
    else:
        port = args.port

    # baudrate
    if args.port is None:
        baudrate = int(input('Please enter baudrate (i.e. 9600,57600)>>'))
    else:
        baudrate = args.baudrate

    # cmd
    if args.command is None:
        cmd = str(input('Please enter command (i.e. *IDN?)'+\
                'or see list in daq_cmd.py>>'))
    else:
        cmd = args.command
        if cmd == str(1):
            cmd = "MEAS:VOLT:DC? (@%s)"%(loc)
            cnvrt = True

    # fname
    if args.fname is None:
        fname = 'out.csv'
    else:
        fname = args.fname

    # delay
    if args.delay is None:
        delay = float(input('Please enter a delay time betweem data collection'+\
                'in secs>>'))
    else:
        delay = args.delay

    # header
    if args.header is None:
        header = ['time [secs]', 'returned [?]']
    else:
        header = args.header


def main():
    ser = rs.RS232(port,baudrate,encode_type='utf-8')
    ser.loop(cmd,header=header,convert=cnvrt,fname=fname,delay=delay)

if __name__ == "__main__":
    main()
