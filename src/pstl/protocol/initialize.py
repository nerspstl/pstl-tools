# initialize.py

def list_ports(list_resources):
    list_resources()

def open_port(port,open_resource,resource_kws):
    resource=open_resource(port,**resource_kws)
    return resource

def choose_port(list_resources,open_resource,
        resource_kws={},list_resources_kws={}):
    """
    listed_resources: a list of available resources
    open_resource: the function called to open choosen resource
    must take 1 argument, port, then any keyword argumnets maybe
    passed via the dictionary resource_kws
    resource_kws: (default {}) list of extra keywords to be passed to
    open the resrouce
    """
    
    strin="R"

    # if refresh
    while strin == "R":
        while strin == "R":
            print('\nAvailable Ports:(Enter "R" for refresh)'\
                    +'\nPort #:\tPort Name')
            print('__________________')

            ## list options to choose from
            listed_resources=list_resources(**list_resources_kws)
            # in case pyserial is used
            if isinstance(listed_resources[0],str):
                pass
            else: # for pyserial
                listed_resources=[None]*len(listed_resources)
                for i,res in enumerate(list_resources(**list_resources_kws)):
                    listed_resources[i]=res[0]
            # loops through options
            for a,aa in enumerate(listed_resources):
                a = a + 1
                print('Option ' + str(a) + ':\t' + aa)
            print('__________________')
            strin = input("Enter Option #:\n>>")
        # end of refresh
        try:
            value=int(strin)
            port = listed_resources[value-1]
        except ValueError:
            port = strin
        except:
            print("Not a valid entry please try again")
            strin="R"

    try:
        print('Trying ' + port)
        resource=open_port(port,open_resource,resource_kws)
        print('\nFound:')
        print(resource)
    except:
        print('Failed ' + port)
        resource=choose_port(list_resources,open_resource,
                resource_kws,list_resources_kws)
    return resource

class Open():
    def __init__(self,list_resources,open_resource,port=None,**kwargs):
        list_resources_kws=kwargs.get('list_resources_kws',{})
        resource_kws=kwargs.get('resource_kws',{})
        # trys to open if given port
        # if fails, it gives you options
        if port is not None:
            try:
                res=open_port(port,open_resource,
                        resource_kw
                        )
            except:
                print("\nFailed to open %s"%(port))
                port=None
        if port is None:
            res=choose_port(list_resources,open_resource,
                    resource_kws,list_resources_kws
                    )


        self.resource=res

        self.write=self.resource.write
        self.read=self.resource.read
        self.close=self.resource.close
        self.open=self.resource.open
