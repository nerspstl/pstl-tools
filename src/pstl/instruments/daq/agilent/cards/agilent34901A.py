
from pstl.instruments.daq.agilent.cards import setuploop as sul

class AGILENT34901A():
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
        channels = sul.__loop_setup(channels,chtype,slot)
            
        self.nchannels=nchannels
        self.slot=slot
        channels[0] = self.list_channels
        self.channel = channels

    def list_channels(self):
        channels=self.channel.location
        chtypes=self.channel.chtype
        for k in range(1,nchannels+1):
            print("\nChannel %s: Type: %s"%(channels[k],chtype[k-1]))




