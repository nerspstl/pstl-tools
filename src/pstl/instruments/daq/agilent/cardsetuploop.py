
from pstl.instruments.daq.agilent import channel

def loop_setup(channels,chtype,slot=None):
    nchannels = int(len(channels)-1)
    bool_list = isinstance(chtype,list)
    if bool_list:
        if len(chtype)==nchannels:
            # do this if same len
            __loop_multi(channels,chtype,slot)
        elif len(chtype)==1:
            # only one type make all that type
            __loop_single(channels,chtype,slot)
        else:
            print("Length of chtype is less than nchannels."\
                    +"Configuring first %i"%(len(chtype)))
            __loop_multi(channels,chtype,slot)
    else:
        try:
            bool_str = isinstance(chtype,str)
            # only one type make all that type
            __loop_single(channels,chtype,slot)
        except TypeError:
            print("Entered '%s' is not valid"%(str(chtype)))
    return channels



def __loop_single(channels,chtype,slot=None):
    """
    Changes the each channel to chtype
    """
    for k in range(1,len(channels)):
        try:
            loc = int(slot*100 + k)
        except:
            loc = int(k)
        channels[k] = channel.CHANNEL(loc,chtype)
    return channels

def __loop_multi(channels,chtypes,slot=None):
    """
    Changes the each channel to its corresponding chtype
    """
    for k in range(1,len(chtype)+1):
        try:
            loc = int(slot*100 + k)
        except:
            loc = int(k)
        chtype = chtypes[k-1]
        channels[k] = channel.CHANNEL(loc,chtype)
    return channels
