import time

import numpy as np
from pstl.instruments.daq.agilent.gpib import Agilent34970A as DAQ
from pstl.instruments.ps.kepco.gpib import BOP_100_1M_488B as PS

def animate():


def sweep(ps,voltages,delay,/,\
        func=None,args=(None),resistance=Nonei,\
        history=False):
    if history:
        output_history=[]
    for j in range(len(voltages)):
        v=voltages[j]
        print(v)
        ps.setVoltage(v)
        time.sleep(delay)
        if func is not None:
            daq_scan=func(*args)
            vPS=daq_scan[0]
            vR=daq_scan[1:]
            current=np.divide(vR,resistance)
            vP=np.subtract(vPS,vR)
            output=np.vstack((vP,current,resistance,vR))
            if history:
                output_history.append(output)
    offVoltage(ps)
    if history:
        return output_history

def offVoltage(ps):
    ps.setVoltage(0)


def setupSupplyVoltages():
    vstart=-1
    vstop=1
    dv=1
    return np.arange(vstart,vstop+dv,dv)

def setupDAQProbeChannels():
    channels=[1,2,9,10,11,12]
    resistance=[1,1,1,1,1]
    return channels,resistance

def scanDAQ(daq,slot,channels):
    output=np.zeros_like(channels,dtype=float)
    for j in range(len(channels)):
        channel=channels[j]
        # splice is to ignore '\n'
        # then convert to float
        output[j]=daq.get(slot,channel)[:-1]
    return output


def main():
    voltage_delay=1 # sec
    
    daq_slot=1
    channels,resistance=setupDAQProbeChannels()

    daq=DAQ("GPIB0::10::INSTR")
    daq.addCardAgilent34901A(daq_slot,20,"VDC")
    ps=PS("GPIB0::6::INSTR")
    supplyVoltages=setupSupplyVoltages()

    
    func=scanDAQ
    args=(daq,slot,channels)
    output=sweep(ps,supplyVoltages,voltage_delay,func,args)
    """
    voltages    Channels
    -1          2       9   10  etc.
    0
    -1

    """
    print(output)


if __name__=="__main__":
    main()
