from pstl.instruments.daq import agilent

def open_port():

    instrument=agilent.agilent34970A.AGILENT34970A()

    return instrument

def main():
    daq=open_port()
    daq.addCardAgilent34901A(1,20,'TCK')
    daq.list_cards()
    daq.card[1].list_channels()
    daq.get(113)
    daq.get(1,13)

if __name__=="__main__":
    main()
