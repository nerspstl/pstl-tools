import time

import numpy as np
from pstl.scripts.janus.utls.agilent import scanDAQRESVDC
from pstl.scripts.janus.utls.agilent import scanDAQVDC
from pstl.scripts.janus.utls.langmuir import langmuir_calc_ps_grnd as lang_calc

def update(k,data,*args):
    # k==channel, aka subplot axes
    vprobe=data[0]
    current=data[1]
    # choose channel data to output
    x_out=vprobe[k]
    y_out=current[k]

    #update any out put args (none here)
    args_out=args
    out={
            'x_out':x_out,
            'y_out':y_out,
            'args_out':args_out
            } 
    return out


def scan(j,ps,daq,slot,channels,voltages,resistance,voltage_delay):
    # j==which iteration of _animate -> jj==which voltage
    lenv=len(voltages)
    jj=np.remainder(j,lenv)
    # then this round of voltage is
    v=voltages[jj]
    # set power supply voltage
    ps.setVoltage(v)
    # if voltage_delay
    if voltage_delay is not None:
        time.sleep(voltage_delay)
    # if resistance is True, probe resisitance
    # elif False, raise error
    # elif None, raise error
    # else, use this list as resistance values for
    if resistance is True:
        r,v=scanDAQRESVDC(daq,slot,channels)
    elif isinstance(resistance,(list,np.ndarray)) and \
            len(resistance)==len(channels)-1:
        r=resistance
        v=scanDAQVDC(daq,slot,channels)
    else: #resistance is False or resistance is None:
        s="'resistance' must be True or a list length of channels minus 1"
        raise ValueError(s)
    # seperate voltages 
    vps=v[0]
    vr=v[1:]

    # perfrom lang analysis
    vprobe,current=lang_calc(vps,vr,r)
    return vprobe,current
    
