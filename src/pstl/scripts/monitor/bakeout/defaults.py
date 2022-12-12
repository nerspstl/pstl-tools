import numpy as np

from pstl.instruments.daq.agilent.gpib import Agilent34970A as DAQ
from pslt.instruments.pg.inficon.model import BPG402_S as PG
from pstl.tools.animate.limit_funcs import between as set_ylimit_temperature

from pstl.scripts.monitor.bakeout.funcs import set_title_pressure

def set_defaults():
    ## set daq and pg ports 
    daq_port="GPIB0::10::INSTR"
    pg_port="COM1"
    ## create daq and pg objects
    daq=DAQ(daq_port)
    pg=PG(pg_port)
    # daq stuff (temperatures)
    channels=range(113,121,1) # 113-120
    nchannels=len(channels)

    # initialize the subplot_kws list of dictionaries for
    # each individual subplot on one figure
    subplot_kws=[None]*(npressure+nchannels)

    # define some temperature ylimit stuff
    temperature_ylimits = [95,135]
    temperature_axhlines = [105,130]
    # define some pressure ylimit stuff
    pressure_ylimits = [-1,1]
    pressure_axhlines = 1e-3

    # set temperature_kws
    for i,ch in enumerate(channels):
        subplot_kws[i+1]={
        'ylabel':       "Temperture [deg C]",
        'start_time':   True,
        'ylimit':       temperature_ylimits,
        'ylimit_style': set_ylimit_temperture,
        'axhline':      temperature_axhlines,
        'func':         daq.getTempTCK,         # pass this in
        'fargs':        ch,
        'title':        "Temperature at %i"%(ch),
        'alerts':       False,
        'alert_check':  alert_temperature,         # add this
        'alert_check_args': (False,0,repeat,delay,recover)
        }

    # set pressure_kw
    subplot_kws[0]={
        'ylabel':       "Pressure [torr]",
        'start_time':   True,
        'ylimit':       pressure_ylimits,
        'ylimit_style': "magnitude",        
        'axhline':      pressure_axhlines,
        'func':         inficon.get,         # write this in
        'fargs':        None,
        'title':        set_title_pressure,
        'alerts':       False,
        'alert_check':  alert_pressure,         # add this
        'alert_check_args': (False,0,repeat,delay,recover)
        }
            
    # create default list with subplot_kws embeded
    defaults={
            'full_screen':  True,
            'alerts':       True,
            'xlabel':       "time [s]",
            'grid':         True,
            'subplot_kw':   subplot_kws
            }

    return defaults
