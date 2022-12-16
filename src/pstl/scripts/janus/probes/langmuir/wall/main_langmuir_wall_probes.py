import time
import json

import numpy as np

from pstl.instruments.daq.agilent.models    import Agilent34970A as DAQ
from pstl.instruments.ps.kepco.models       import BOP_100_2D_802E as PS
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
        probe_locations=[0,10,40,100,133]   # [cm]
        #r_channel=[2]
        channels=ps_channel+r_channel
        resistance=True
        #supplyVoltages
        vstart=-20
        vstop=30
        dv=1
        supply_voltages=np.arange(vstart,vstop+dv,dv)
        style='step'
        #style='trace'
        params={
                'voltage_delay':voltage_delay,
                'daq_slot':daq_slot,
                'ps_channel':ps_channel,
                'r_channels':r_channel,
                'channels':channels,
                'resistance':resistance,
                'supply_voltages':supply_voltages,
                'manual':False,
                'debug':True,
                'probe_locations':probe_locations,
                'style':style
                }
    return params

def setTitle(k,ax,probe_location):
    i=k+1
    s="Probe %i: @%icm"%(i,probe_location[k])
    ax.set(title=s)


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
    debug=params.get("debug",False)
    style=params.get("style","step")

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
        # for GPIB
        #ps=PS("GPIB0::6::INSTR")
        # for socket
        ps=PS("TCPIP0::ners-plasma-kepco.engin.umich.edu::5025::SOCKET")

    # setup figure for data
    if style.upper()=="STEP":
        updatelimit=len(supply_voltages)
        update_func=sweep.update
        get_data_func=sweep.scan
        updateline=True
    elif style.upper()=="TRACE":
        updatelimit=1
        update_func=sweep.update_trace
        get_data_func=sweep.trace
        updateline=False
    else:
        raise ValueError("Not a known style '%s'"%(style))

    kwargs={
            "func":update_func,
            "xlabel":"Voltage [V]",
            "ylabel":"Current [A]",
            "updatelimit":updatelimit,
            "reorderx":True,
            "updateline":updateline,
            "full_screen":True,
            "title":setTitle
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
                manual,debug)
        # animate kwargs dict
        animate_kwargs={
                'title_args':(params['probe_locations'],),
                }
        # pass dict to monitor for animate function
        kwargs={
                "fargs":(get_data_func,args,animate_kwargs)
                }
        langmuir.monitor(**kwargs)
    except KeyboardInterrupt:
        print("exiting ...")
    if manual is True:
        pass
    else:
        #ps.setVoltage(0)
        ps.close()
    exit_handler(save,langmuir)


if __name__=="__main__":
    main()
