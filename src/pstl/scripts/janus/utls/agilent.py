import numpy as np

# some functions are dependent on classes defined elsewhere
# here they are passed in and functions are called

def setupDAQProbeChannels():
    channels=[1,2,9,10,11,12]
    resistance=[1,1,1,1,1]
    return channels,resistance

def scanDAQ(daq,slot,channels,func=None):
    if func is None:
        func=daq.get
    output=np.zeros_like(channels,dtype=float)
    for j in range(len(channels)):
        channel=channels[j]
        # splice is to ignore '\n'
        # then convert to float
        location=int(np.add(np.multiply(slot,100),channel))
        output[j]=func(location)[:-1]
    return output

def scanDAQRESVDC(daq,slot,channel):
    r=scanDAQ(daq,slot,channel,daq.getRes)
    vr=scanDAQ(daq,slot,channel,daq.getVDC)
    return r,vr

def scanDAQVDC(daq,slot,channel):
    return scanDAQ(daq,slot,channel,daq.getVDC)
