import serial

def main():
    # other daq
    #port = "COM7"
    #baudrate=57600
    port = "COM5"
    baudrate=9600
    readtimeout=1
    ser = serial.Serial(port, baudrate,timeout=readtimeout)

    ser.write('*IDN?\n'.encode('utf-8'))

    s = ser.readline()
    # should print:
    # b'HEWLETT-PACKARD,34970A,0,12-1-2\r\n'
    print(s)

if __name__ == "__main__":
    main()
