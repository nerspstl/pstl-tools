
from pstl.instruments.daq.agilent.cards import channel

def __loop_setup(channels,chtype,nslots=None):
    nchannels = int(len(channels)-1)
    bool_list = isinstance(chtype,list)
    if bool_list:
        if len(chtype)==nchannels:
            # do this if same len
            __loop_multi(channels,chtype,nslots)
        elif len(chtype)==1:
            # only one type make all that type
            __loop_single(channels,chtype,nslots)
        else:
            print("Length of chtype is less than nchannels."\
                    +"Configuring first %i"%(len(chtype))i)
            __loop_multi(channels,chtype,nslots)
    else:
        bool_str = isinstance(chtype,str)
        try bool_str:
            # only one type make all that type
            __loop_single(channels,chtype,nslots)
        except TypeError:
            print("Entered '%s' is not valid"%(str(chtype)))
    return channels



def __loop_single(channels,chtype,nslots=None):
    """
    Changes the each channel to chtype
    """
    for k in range(1,len(channels)+1):
        try:
            loc = int(nslot*100 + k)
        except:
            loc = int(k)
        channels[k-1] = channel.Channel(loc,chtype)
    return channels

def __loop_multi(channels,chtypes,nslots=None):
    """
    Changes the each channel to its corresponding chtype
    """
    for k in range(1,len(chtype)+1):
        try:
            loc = int(nslot*100 + k)
        except:
            loc = int(k)
        chtype = chtypes[k-1]
        channels[k-1] = channel.Channel(loc,chtype)
    return channels
