import time
import argparse

import numpy as np
import serial

parser = argparse.ArgumentParser()
parser.add_argument("-f","--fname",\
        help="path/to/filename ie dir/out.csv",type=str)
parser.add_argument("-d","--delay",\
        help="delay time between data collection",type=float)
parser.add_argument("-p","--port",\
        help="port number ie Windows 'COM5',Linux ttyS0",type=str)
parser.add_argument("-s","--string",\
        help="input command to run in loop",action="store_true")
args = parser.parse_args()


def getData():

    # define variables
    if args.port is None:
        port = "COM8"
    else:
        port = args.port
    baudrate = 2400
    timeout = 1


    # define encoding type
    etype = "ascii"
    # define end bit
    ebit = "\n"
    # define return bit
    rbit = "\r"

    # time delay in seconds
    if args.delay is None:
        delay = 1
    else:
        delay = args.delay

    # open serial
    ser = serial.Serial(port,baudrate,timeout=timeout)

    # input syntax
    if args.string:
        s = input('Please input code to run in cnt loop>>')
    else:
        s = "=RV"#input('Please input code to run in cnt loop>>')

    # infinite string variable
    ISTR = []
    RSTR = []
    TSTR = []

    # declare start time
    start_time = None

    # try:
    try:
        print("collecting data...")
        print("press Ctrl+C to stop")
        while True:
            # get time
            t = time.time()
            if start_time is None:
                start_time = t
            dt  = t - start_time    # [secs]

            # write input, save num of bits written
            nbits = ser.write((s+rbit).encode(etype))

            # read until ebit first return command input
            istr = ser.read_until(ebit.encode(etype))
            # read until ebit of returned result
            rstr = ser.read_until(ebit.encode(etype))

            # print returned string
            print(dt)
            print(istr)
            print(rstr)

            # append list
            ISTR.append(istr)
            RSTR.append(rstr)
            TSTR.append(dt)

            # time delay
            if delay is not None:
                time.sleep(delay-((time.time()-start_time)%delay))
    except KeyboardInterrupt:
        print("Exitting loop..")

    # close port
    print("closing port")
    ser.close()
    print("converting data from bytes to strings")
    RSTR=[x.decode(etype) for x in RSTR]
    #print(RSTR.decode(etype))
    #print(RSTR)

    return ISTR, RSTR, TSTR

def cnvrtData(STR):
    slen = len(STR)
    data = np.zeros([slen,])
    for k in range(slen):
        s = STR[k].split("=",1)[1][0:6].split("-",1)
        data[k] = float(s[0]+"e-"+s[1])
    return data

def saveData(L,fname):
    Llen = len(L)
    l = None
    cnt = True
    for k in range(Llen):
        lnew = len(L[k])
        if l is not None:
            if l != lnew:
                print("data is not same lengths")
                cnt = False
        l = lnew
    if cnt:
        try:
            f = open(fname,'w')
        except:
            print("file permission denied.")
            input("Press enter to try again.")
            f = open(fname,'w')
        for i in range(l):
            for j in range(Llen):
                f.write('%.15e'%(L[j][i]))
                if i != l:
                    f.write(',')
            f.write('\n')
        f.close()
    print("data saved in %s"%(fname))


def main():
    # define output filename
    if args.fname is None:
        fname = "test_out.csv"
    else:
        fname = args.fname
    ISTR, RSTR, TSTR = getData()
    RDATA = cnvrtData(RSTR)
    TDATA = np.array(TSTR)
    saveData([TDATA,RDATA],fname)


if __name__ == "__main__":
    main()
