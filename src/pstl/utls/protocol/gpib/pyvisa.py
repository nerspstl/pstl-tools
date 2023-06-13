from pstl.utls.protocol.gpib import initialize as init

class Open():
    def __init__(self,port=None):

        # trys to open if given port
        # if fails, it gives you options
        if port is not None:
            try:
                res=init.open_port(port)
            except:
                print("\nFailed to open %s"%(port))
                port=None
        if port is None:
            res=init.choose_port()


        self.visa=res

        self.port=self.visa.resource_name
        
        self.write=self.visa.write
        self.read=self.visa.read
        self.query=self.visa.query
