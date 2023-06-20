
from pstl.instruments.daq.agilent import utls as sul

class Agilent34901A():
    def __init__(self,slot=None,nchannels=20,chtype=None):

        """
        creates a object for the card agilent 34901A.
        20 Channels 
        (Note channel[0] is not an acual channel but will 
        display the list of channels and thier configured type.)
        """
        self.name="agilent34901A"
        self.type="agilent card"
        channels = [None]*(nchannels+1)
        # check of chtypes was a list
        channels = sul.loop_setup(channels,chtype,slot)
            
        self.nchannels=nchannels
        self.slot=slot
        channels[0] = self.list_channels
        self.channel = channels

    def list_channels(self):
        nchannels=self.nchannels
        print()
        for k in range(1,nchannels+1):
            channel=self.channel[k].location
            chtype=self.channel[k].chtype
            print("Channel %s: Type: %s\n"%(str(channel),str(chtype)))




