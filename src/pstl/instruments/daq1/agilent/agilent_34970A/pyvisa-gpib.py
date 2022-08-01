import initialize as init

import .commands as cmds

class AGILENT_34970A():
    def __init__(self,port=None):
        # trys to open if given port
        # if fails, it gives you options
        while port is not None:
            try:
                res=init.open_port(port)
            except:
                print("Failed to open %s"%(port))
                port=None
        if port is None:
            res=init.choose_port()

        self.visa=res
        self.write=self.visa.write
        self.read=self.visa.read
        self.query=self.visa.query
    
    def getVDC(self,loc):
        return self.query(cmds.cmdGetVoltageDC(loc))

    def getVAC(self,loc):
        return self.query(cmds.cmdGetVoltageAC(loc))

    def getTempTCK(self,loc):
        return self.query(cmds.cmdGetTemperatureTCK(loc))
