from pstl.instruments.daq import agilent

def open_port(port=None):

    instrument=agilent.agilent34970A.AGILENT34970A(port)

    return instrument

def main():
    port="GPIB0::10::INSTR"
    port=None
    daq=open_port(port)
    daq.addCardAgilent34901A(1,20,'TCK')
    daq.list_cards()
    #daq.card[1].list_channels()
    r=daq.get(113)
    print(r)
    r=daq.get(1,13)
    print(r)

if __name__=="__main__":
    main()
