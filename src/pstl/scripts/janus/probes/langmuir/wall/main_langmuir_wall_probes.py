import time
import json

import numpy as np

from pstl.instruments.daq.agilent.models    import Agilent34970A as DAQ
from pstl.instruments.ps.kepco.models       import BOP_100_1M_488B as PS
from pstl.tools.animate.monitor             import Figure as FIG 
from pstl.scripts.janus.utls                import sweep
from pstl.scripts.janus.utls.agilent        import scanDAQRESVDC
from pstl.scripts.janus.utls.agilent        import scanDAQRES
from pstl.scripts.janus.utls.agilent        import scanDAQVDC

def exit_handler(save,obj):
    if save:
        obj.save_all()

def get_parameters(fname=None):
    if fname is not None:
        with open(fname,'r') as f:
            params=jsons.load(fname)

    else:
        voltage_delay=1
        daq_slot=1
        ps_channel=[1]
        r_channel=[2,9,10,11,12]
        #r_channel=[2]
        channels=ps_channel+r_channel
        resistance=True
        #supplyVoltages
        vstart=-20
        vstop=30
        dv=1
        supply_voltages=np.arange(vstart,vstop+dv,dv)
        params={
                'voltage_delay':voltage_delay,
                'daq_slot':daq_slot,
                'ps_channel':ps_channel,
                'r_channels':r_channel,
                'channels':channels,
                'resistance':resistance,
                'supply_voltages':supply_voltages,
                'manual':True
                }
    return params



def main():
    # get parameters 
    parameters_fname=None   # if not None, read in this json file
    params=get_parameters(parameters_fname)

    # retrive needed variables from parameters and set standard defaults
    voltage_delay=params.get('voltage_delay',1) # seconds
    daq_slot=params.get('daq_slot',1) 
    channels=params.get('channels',None)
    resistance=params.get('resistance',True) # True: will probe
    supply_voltages=params.get('supply_voltages',None)
    nrows=params.get("nrows",5)
    ncols=params.get("ncols",1)
    save=params.get("save",True)
    manual=params.get("manual",False)

    # check required inputs and raise error if not provided
    if channels is None: 
        raise ValueError("'channels' parameter was not defined")
    if supply_voltages is None: 
        raise ValueError("'supply_voltages' parameter was not defined")
    

    # setup DAQ class and add card class
    daq=DAQ("GPIB0::10::INSTR")
    daq.addCardAgilent34901A(daq_slot,20,"VDC")
    # setup power supply class
    if manual is True:
        ps=None
    else:
        ps=PS("GPIB0::6::INSTR")

    # setup figure for data
    kwargs={
            "func":sweep.update,
            "xlabel":"V [V]",
            "ylabel":"I [A]",
            "updatelimit":len(supply_voltages),
            "reorderx":True,
            "updateline":True,
            "full_screen":True
            }
    langmuir=FIG(nrows,ncols,**kwargs)
    """
    voltages    Channels
    -1          2       9   10  etc.
    0
    -1

    """

    # get resistance before stating loop
    rstr='R'
    if resistance is True:
        while rstr.upper()=='R':
            resistance=scanDAQRES(daq,daq_slot,channels[1:])
            for ch,value in zip(channels[1:],resistance):
                print("Channel %i: %f ohms"%(ch,value))
            rstr=input("\nPress anything to continue or 'R' to retry>>")
        # set daq back to vdc so no errors occur
        vr=scanDAQVDC(daq,daq_slot,channels[1:])


    # run actual program
    print("running ...")
    print("close figure to stop and save data")
    try:
        # args for scan function in animate
        args=(ps,daq,daq_slot,channels,
                supply_voltages,resistance,
                voltage_delay,
                manual)
        # pass dict to monitor for animate function
        kwargs={
                "fargs":(sweep.scan,args)
                }
        langmuir.monitor(**kwargs)
    except KeyboardInterrupt:
        print("exiting ...")
    if manual is True:
        pass
    else:
        ps.setVoltage(0)
    exit_handler(save,langmuir)


if __name__=="__main__":
    main()
