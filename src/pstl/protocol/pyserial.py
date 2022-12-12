from serial                     import Serial   as open_resource
from serial.tools.list_ports    import comports as list_resources

from pstl.protocol.initialize   import Open

class Pyserial(Open):
    def __init__(self,port=None,**kwargs):
        # save protocal type
        self.protocol="pyserial"

        Open.__init__(self,list_resources,open_resource,port,**kwargs)
