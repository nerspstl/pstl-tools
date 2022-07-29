import time
import argparse

import serial

try:
    import defaults_arduino as defaults
except:
    print("defaults_arduino.py file not found.\n"\
            +"Please create file with parameters:"\
            +"fname,delay,port,resolution,ratio,baudrate"\
            +"")

parser = argparse.ArgumentParser()
parser.add_argument("-f","--fname",\
        help="path/to/filename ie dir/out.csv",type=str)
parser.add_argument("-d","--delay",\
        help="delay time between data collection",type=float)
parser.add_argument("-p","--port",\
        help="port number ie Windows 'COM5',Linux ttyS0",type=str)
parser.add_argument("-r","--resolution",\
        help="Volts/bits ie 5/1024",type=float)
parser.add_argument("-R","--ratio",\
        help="voltage divider ratio ie 10/4.3956",type=float)
parser.add_argument("-b","--baudrate",\
        help="baudrate of serial ie 9600",type=int)
args = parser.parse_args()

# resolution [Volts/bits] 
# ie 5/1024
if args.resolution is not None:
    resolution = args.resolution
else:
    resolution = defaults.resolution

# voltage divider ratio
if args.ratio is not None:
    ratio = args.ratio
else:
    ratio = defaults.ratio

# com port of pttyS#
if args.port is not None:
    port = args.port
else:
    port = defaults.port

# baudrate
if args.baudrate is not None:
    baudrate = args.baudrate
else:
    baudrate = defaults.baudrate

# save filename
if args.fname is not None:
    fname = args.fname
else:
    fname = defaults.fname

# delay time between each read
if args.delay is not None:
    delay = args.delay
else:
    delay = defaults.delay

def openSerial():
    ser = serial.Serial(port,baudrate,timeout=1)
    return ser

def openFile(fname):
    try:
        f = open(fname,'w')
    except:
        print("file permission denied.")
        input("Press enter to try again.")
        f = openFile(fname)
    return f


def getData(display=True):

    # open serial port 
    ser = openSerial()

    # decode type
    etype = 'utf-8'

    # infinite string variable
    data = []
    row = []

    # add label row
    data.append(['time [secs]','value [0-1023]',\
            'V2 [Volts]','(V1+V2) [Volts]','Pressure [torr]'])

    # declare start time
    start_time = None

    # string to encode
    STR = "=RV\r\n".encode(etype)

    print("collecting data...")
    print("press Ctrl+C to stop\n")
    while True:
        try:

            # write to get value
            nbits = ser.write(STR)

            # read 1 line and decode
            value = ser.readline().decode(etype)

            # fix if blank read
            if value == '':
                continue

            # get time
            t = time.time()
            if start_time is None:
                start_time = t
            dt  = t - start_time    # [secs]

            # drop end termination \r\n 
            value = float(value)


            # converstion from str2int for voltage over
            # 2nd resistor in volatage divider
            vout = value*resolution

            # conversion from dV over 2nd resistor
            # to the total V
            Vout = vout*ratio

            # grab exponent
            expo = -int(Vout)

            #p = float(str(10*(1-VOUT+expo))+"e-"+str(expo))

            # calculate manissa
            manissa = 10*(1-Vout-expo)

            # calculate pressure from exponent and manissa
            pressure = manissa*10**(expo)

            # if disply
            if display:
                print("time=%.2f [secs]\nreturned=%.0f\n"\
                        "vout=%.4f [V]\nVout=%.4f [V]\npressure=%.1e [torr]\n"\
                        %(dt,value,vout,Vout,pressure))

            # append list
            row = [dt,value,vout,Vout,pressure]
            data.append(row)

            # time delay
            if delay is None or delay == 0:
                pass
            else:
                time.sleep(delay-((time.time()-start_time)%delay))
        except KeyboardInterrupt:
            print("Exitting loop...")
            break

    # close port
    print("closing port")
    ser.close()

    return data

def saveData(data,fname):
    npts = len(data)
    ncols = len(data[0])

    # try to open file
    f = openFile(fname)

    # save data
    for i in range(npts):
        for j in range(ncols):
            if i == 0:
                f.write('%s'%(data[i][j]))
            else:
                f.write('%.15e'%(data[i][j]))
            if j != ncols-1:
                f.write(',')
        f.write('\n')
    f.close()
    print("data saved in %s"%(fname))

def main():
    data = getData()
    saveData(data,fname)


if __name__ == "__main__":
    main()
