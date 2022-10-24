from pstl.instruments.daq import agilent

def open_port(port=None):

    instrument=agilent.gpib.Agilent34970A(port)

    return instrument

def main():
    port="GPIB0::10::INSTR"
    card=1
    channel=13
    location=int(card*100+channel)
    port=None
    daq=open_port(port)
    daq.addCardAgilent34901A(1,20,'TCK')
    daq.list_cards()
    #daq.card[1].list_channels()
    print(daq.card[card].channel[channel].getcmd)
    r=daq.get(location)
    print("Temperature %.2f degC"%(float(r)))
    r=daq.get(card,channel)
    print("Temperature %.2f degC"%(float(r)))

if __name__=="__main__":
    main()
