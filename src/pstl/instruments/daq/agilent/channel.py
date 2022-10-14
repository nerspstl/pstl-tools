from pstl.instruments.daq.agilent import commands as cmds


class CHANNEL():
    def __init__(self,location,chtype="VDC"):
        self.location=location
        self.change(location,chtype)

        
    def change(self,location,chtype):
        """
        Changes channel type
        """
        if chtype=="VDC":
            get=cmds.cmdGetVoltageDC(self.location)
        elif chtype=="VAC":
            get=cmds.cmdGetVoltageAC(self.location)
        elif chtype=="TCK":
            get=cmds.cmdGetTemperatureTCK(self.location)
        elif chtype=="RES":
            get=cmds.cmdGetResistance(self.location)
        else:
            print("Channel Type (chtype) not set to known value at Channel %s"%(str(self.location)))
            get=None

        self.chtype=chtype
        self.getcmd=get
