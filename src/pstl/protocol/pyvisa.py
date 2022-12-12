from pyvisa                     import ResourceManager

from pstl.protocol.initialize   import Open

class Pyvisa(Open):
    def __init__(self,port=None,**kwargs):
        # save protocal type
        self.protocol="pyvisa"

        # create functions to list and open pyvisa compatibile components
        rm=ResourceManager()
        list_resources=rm.list_resources
        open_resource=rm.open_resource

        # initialize port
        Open.__init__(self,list_resources,open_resource,port,**kwargs)

        self.port=self.resource.resource_name 
        self.query=self.resource.query
