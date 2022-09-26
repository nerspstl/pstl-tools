import pyvisa as visa


rm = visa.ResourceManager()

def choose_port():
    print('\n')
    print(rm)

    # List ports
    # First time
    print('\nAvailable Ports:(Enter "R" for refresh)\nPort #:\tPort Name')
    print('__________________')
    a = 0
    for aa in rm.list_resources():
        a = a + 1
        print('Port ' + str(a) + ':\t' + aa)
    print('__________________')
    strin = input("Enter Port #:\n>>")
    # end of first

    # if refresh
    while strin == "R":
        print('\nAvailable Ports:(Enter "R" for refresh)\nPort #:\tPort Name')
        print('__________________')
        a = 0
        for aa in rm.list_resources():
            a = a + 1
            print('Port ' + str(a) + ':\t' + aa)
        print('__________________')
        strin = input("Enter Port #:\n>>")
    # end of refresh
    port = rm.list_resources()[int(strin)-1]
    print('port = ' + port)

    return port

def open_port(port):
    myinstrument = rm.open_resource(port)
    print(myinstrument)
    return myinstrument

def get_id(myinstru):
    returned = myinstru.query("*IDN?")
    print(returned)
    return returned

def main():
    port = choose_port()
    myinstru = open_port(port)
    returned = get_id(myinstru)


if __name__ == "__main__":
    main()
