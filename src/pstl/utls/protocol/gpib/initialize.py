import pyvisa as visa

rm = visa.ResourceManager()

def list_ports():
    rm.list_resources()

def open_port(port):
    resource=rm.open_resource(port)
    return resource

def choose_port():
    
    strin="R"

    # if refresh
    while strin == "R":
        while strin == "R":
            print('\nAvailable Ports:(Enter "R" for refresh)'\
                    +'\nPort #:\tPort Name')
            print('__________________')
            a = 0
            for aa in rm.list_resources():
                a = a + 1
                print('Port ' + str(a) + ':\t' + aa)
            print('__________________')
            strin = input("Enter Port #:\n>>")
        # end of refresh
        try:
            port = rm.list_resources()[int(strin)-1]
        except:
            print("Not a valid entry please try again")
            strin="R"

    print('Trying ' + port)
    resource=open_port(port)
    print('\nFound:')
    print(resource)
    return resource

