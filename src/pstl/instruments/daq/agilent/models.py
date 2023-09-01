from typing import Any

import numpy as np

from pstl.utls.protocol.gpib.pyvisa import Open
from pstl.instruments.daq.agilent import cards
from pstl.instruments.daq.agilent import commands as cmds

class Agilent34970A(Open):
    def __init__(self,port=None):

        Open.__init__(self,port)

        self.class_name="agilent34970A"
        self.type="daq"

        self.name=self.query("*IDN?")

        card : list[Any] = [None]*4    # three potential cards and 0 is list cards
        card[0]=self.list_cards
        self.card=card
    
    def getVDC(self,loc):
        return self.query(cmds.cmdGetVoltageDC(loc))

    def getVAC(self,loc):
        return self.query(cmds.cmdGetVoltageAC(loc))

    def getTempTCK(self,loc):
        return self.query(cmds.cmdGetTemperatureTCK(loc))

    def getRes(self,loc):
        return self.query(cmds.cmdGetResistance(loc))


    def addCard(self):
        # add interative later
        pass


    def addCardAgilent34901A(self,slot,nchannels,chtype):

        self.card[slot]=\
        cards.Agilent34901A(slot,nchannels,chtype)


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
        Gets the preset value for that slot/channel combo
        if only location then 'slot#,channel##'
        if both location and channel then location is slot
        """
        if channel is None:
            loc=location
            location=int(np.floor(loc/100))
            channel = int(loc-location*100)
        cmd=self.card[location].channel[channel].getcmd
        return self.query(cmd)
