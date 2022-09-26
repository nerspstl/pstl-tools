import math

from pstl.instruments.daq.agilent import initialize as init
from pstl.instruments.daq.agilent import cards
from pstl.instruments.daq.agilent import commands as cmds

class AGILENT34970A():
    def __init__(self,port=None):
        # trys to open if given port
        # if fails, it gives you options
        while port is not None:
            try:
                res=init.open_port(port)
            except:
                print("\nFailed to open %s"%(port))
                port=None
        if port is None:
            res=init.choose_port()

        self.name="agilent34970A"
        self.type="daq"
        self.visa=res
        self.write=self.visa.write
        self.read=self.visa.read
        self.query=self.visa.query

        card = [None]*4    # three potential cards and 0 is list cards
        card[0]=self.list_cards
        self.card=card
    
    def getVDC(self,loc):
        return self.query(cmds.cmdGetVoltageDC(loc))

    def getVAC(self,loc):
        return self.query(cmds.cmdGetVoltageAC(loc))

    def getTempTCK(self,loc):
        return self.query(cmds.cmdGetTemperatureTCK(loc))


    def addCard(self):
        # add interative later
        pass


    def addCardAgilent34901A(self,slot,nchannels,chtype):

        self.card[slot]=\
        cards.agilent34901A.AGILENT34901A(slot,nchannels,chtype)


    def list_cards(self):
        card=self.card
        print()
        for k in range(1,len(card)):
            try:
                print("Slot: %s\nType: %s\nChannels: %s\n"%(str(k),str(card[k].name),str(card[k].nchannels)))
                self.card[k].channel[0]()
            except:
                print("Slot: %s\nType: None\n\n"%(str(k)))

    def get(self,location,channel=None):
        """
        if only location then 'slot,##channel'
        if both location and channel then location is slot
        """
        if channel is None:
            loc=location
            location=int(math.floor(loc/100))
            channel = int(loc-location*100)
        cmd=self.card[location].channel[channel].getcmd
        return self.query(cmd)
