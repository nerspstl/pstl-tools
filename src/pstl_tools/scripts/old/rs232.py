import time

import serial

class RS232():
    def __init__(self,/,
            port="COM5",baudrate=2400,timeout=1,encode_type="ascii",end_bit="\n",return_bit="\r"):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.encode_type = encode_type
        self.end_bit = end_bit
        self.return_bit = return_bit
        self.connected = False

    def open(self):
        try:
            self.ser = serial.Serial(port=self.port,baudrate=self.baudrate,timeout=self.timeout)
            self.connected = self.ser.is_open
        except:
            print("cannot open port %s"%(self.port))

    def write(self,cmd):
        try:
            self.ser.write((cmd+self.return_bit+self.end_bit).encode(self.encode_type))
        except:
            print("unable to write to serial")

    def read(self,/,end_bit=None):
        if end_bit is None:
            end_bit = self.end_bit

        return self.ser.read_until(end_bit.encode(self.encode_type))

    def close(self):
        self.ser.close()
        self.connected = self.ser.isOpen()

    def saveData(self,data,fname="out.csv"):
        # get lens of data
        lenx = len(data)
        leny = len(data[0])

        # try opening file to save to
        # protects from loss of data
        try:
            f = open(fname,'w')
        except:
            print("file permission denied.")
            input("Press enter to try again."+\
                    "Or ctrl+c to quit.")
            f = open(fname,'w')

        def check(d):
            if isinstance(d, float):
                t = float
            elif isinstance(d, str):
                t = str
            elif isinstance(d, int):
                t = int
            else:
                print('ERROR UNKNOWN TYPE')
                t = None

            return t

        # start loop to save data
        for i in range(lenx):
            for j in range(leny):
                d = data[i][j]
                ftype = check(d)
                if ftype == float:
                    f.write('%.15e'%(d))
                elif ftype == str:
                    f.write('%s'%(d))
                elif ftype == int:
                    f.write('%i'%(d))
                else:
                    print('not valied type')
                if j != leny-1:
                    f.write(',')
            f.write('\n')
        f.close()
        print("data saved in %s"%(fname))

    def loop(self,/,cmd=None,convert=False,header=None,\
            save=True,fname="out.csv",\
            delay=1,start_time=None,\
            display=True,skip=None,repeat=None):

        # check if connected
        if self.connected == False:
            self.open()
        if cmd is None:
            cmd = input('Please input code to run in inf loop>>')
        RSTR = []
        TSTR = []

        # repeat save for one command 
        if repeat is None:
            repeat = 0

        # save names from class
        write = self.write
        read = self.read
        encode_type = self.encode_type

        print('collecting data...')
        while True:
            try:
                # write to get value
                nbits = write(cmd)

                # get time
                t = time.time()
                if start_time is None:
                    start_time = t
                dt = t - start_time # [secs]


                # skip a return per command
                if skip is not None:
                    for k in range(skip):
                        rstr = read()

                for k in range(repeat+1):
                    rstr = read()

                    if display:
                        print("time=%.2f [secs]"%(dt))
                        print(rstr)

                    RSTR.append(rstr)
                    TSTR.append(dt)

                # time delay
                if delay is None or delay == 0:
                    pass
                else:
                    time.sleep(delay-((time.time()-start_time)%delay))
            except KeyboardInterrupt:
                print("Exitting loop..")
                break

        if self.connected == True:
            print("closeing port")
            self.close()

        print("converting data from bytes to strings")
        if self.return_bit is not None:
            RSTR=[x.decode(encode_type)[:-2] for x in RSTR]
        else:
            RSTR=[x.decode(encode_type)[:-1] for x in RSTR]

        # single data
        datalen = len(TSTR)
        start = 0
        if header is not None:
            try:
                headerlenx = len(header)
                headerleny = len(header[0])

                if headerlenx == 2:
                    data = [None]*(datalen+1)
                    data[0] = header
                    start = 1
                else:
                    print('Header is not 1x2 list.\nSkipping header...')
                    data = [None]*datalen
            except:
                print('Header is not 1x2 list.\nSkipping header...')
                data = [None]*datalen
        else:
            data = [None]*datalen

        if convert:
            for k in range(datalen):
                data[k+start] = [TSTR[k],float(RSTR[k])]
        else:
            for k in range(datalen):
                data[k+start] = [TSTR[k],RSTR[k]]

        # save if fname
        if save:
            self.saveData(data,fname=fname)

        return data

