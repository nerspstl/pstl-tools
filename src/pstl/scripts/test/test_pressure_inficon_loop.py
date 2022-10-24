import time

import pyvisa as visa
import numpy as np

rm = visa.ResourceManager()

PORT = "GPIB::10::INSTR"

daq = rm.open_resource(PORT)


def conversion(V,c=6.304):
    """
    converts Voltage to pressure for Inficon 
    PSG550,PSF552,PSG554
    c=6.143 [mbar]
    c=2.287 [\mu-bar]
    c=6.304 [torr] (default)
    c=2.448 [mtorr] [micron]
    c=3.572 [Pa]
    c=7.429 [kPa]
    """
    exp = np.multiply(0.778,np.subtract(V,c))
    return np.power(10,exp)

cmd = "MEAS:VOLT:DC? (@106)"
delay = 10
fname = "daq_inficoni_005.csv"

def get_pressure(cmd):

    V = float(daq.query(cmd)[:-1])

    p = conversion(V)

    return p

def loop():

    RSTR = []
    TSTR = []


    start_time = None
    print()

    while True:
        try:
            # get time
            t = time.time()
            if start_time is None:
                start_time = t
            dt = t - start_time # [secs]


            # write to get value
            p = get_pressure(cmd)

            print("time=%.2f [secs]"%(dt))
            print("Pressure=%.2e [torr]"%(p))
            print()

            RSTR.append(p)
            TSTR.append(dt)

            # time delay
            if delay is None or delay == 0:
                pass
            else:
                time.sleep(delay-((time.time()-start_time)%delay))
        except KeyboardInterrupt:
            print("Exitting loop..")
            break

    RSTR = np.array([RSTR])
    TSTR = np.array([TSTR])



    data = np.concatenate((TSTR.transpose(),RSTR.transpose()),axis=1)

    return data

def saveCSV(fname,data):
    print("saving %s..."%(fname))
    header="Time [s], Pressure [torr]"
    np.savetxt(fname,data,header=header,delimiter=",")


data = loop()


saveCSV(fname,data)
