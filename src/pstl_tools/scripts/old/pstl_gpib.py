import os

import pyvisa as visa

class TDS640a:
    
    def __init__(self, port = None, mydir = None, myfile = None, channel = None):
         
        # indicates which backend is being used
        rm = visa.ResourceManager()
        print('\n')
        print(rm)

        a = 0
        if port is None:
            a = a + 1
        if channel is None:
            a = a + 1
        if myfile is None:
            a = a + 1
        if mydir is None:
            a = a + 1

        if a != 0:
            print('Not enough arguments passed\nPlease follow prompt\n')
            self.enter()
        else:
            if isinstance(port, int):
                print('\nEntered integer for port, assumeing that meant port #')
                print('\nAvailable Ports:\nPort #:\tPort Name')
                print('__________________')
                b = 0
                for aa in rm.list_resources():
                    b = b + 1
                    print('Port ' + str(b) + ':\t' + aa)
                print('__________________')
                port = rm.list_resources()[port-1]
                print('Using ' + str(port))
            self.gpib = rm.open_resource(port)
            
            self.port = port
            self.myfile = myfile
            self.mydir = mydir
            self.channel = channel  

        # print where
        print('\nWorking with ' + self.port)
        print('Working with ' + self.myfile)
        print('Working in ' + self.mydir)
        print('Working with ' + self.channel)

        print('\n')
        print('General (Floppy and computer) Available  commands:')
        print('changegpibport, changemydir, changemyfile, changechannel')
        print('\n')
        print('Other (Floppy) Available  commands:')
        print('save, delete, cwd, cwdQ, mkdir, rmdir, dirQ ')
        print('\n')
        print('Suggested (computer) Available  commands:')
        print('acquire, saveplt, getwfm ')


    def gpibport(self, PORT = None):
        #import pyvisa as visa 
        # indicates which backend is being used
        rm = visa.ResourceManager()
        try:
            if PORT is None:
                PORT = self.port
            # opens declared resource
            myinstrument = rm.open_resource(PORT)
            return myinstrument
        except IndexError:
            return 0

    def save(self, CHANNEL = None, PORT = None, MYFILE = None):
            
        # NOTES for GPIB TDS640a
        #<filename> = filename of up to 8 characters and can
        #be followed by a period (“.”) and a 3-character extension.
        try:
            if PORT is None:
                PORT = self.port
            if CHANNEL is None:
                CHANNEL = self.channel
            if MYFILE is None:
                MYFILE = self.myfile
            # SAVES WAVEFORM
            # SAVE:WAVEFORM <CH#,MATH#>,"FILEPATH/FILENAME.WFM>"
            #	i.e. (current Directory) SAVE:WAVEFORM CH1,"TEKCH1.WFM"
            #	i.e. (path to directory) SAVE:WAVEFORM CH1,"fd0:/LANG/LANG1/TEKCH1.WFM"
            scope = self.gpibport(PORT)
            scope.write('SAVE:WAVEFORM ' + CHANNEL + ',"' + MYFILE + '"')
            
        except IndexError:
            return 0

    def delete(self, PORT = None, MYFILE = None):
        try:
            if PORT is None:
                PORT = self.port
            if MYFILE is None:
                MYFILE = self.myfile
            # Delete FILE
            # FILESYSTEM:DELTE "<FilePath>"
            scope = self.gpibport(PORT)
            scope.write('FILESYSTEM:DELETE "' + MYFILE + '"')
            
        except IndexError:
            return 0

    def cwdQ(self, PORT = None):
        try:
            if PORT is None:
                PORT = self.port
            # Inquieres what is working directory
            # FILESYSEM:CWD?
            scope = self.gpibport(PORT)
            out = scope.query('FILESYSTEM:CWD?')
            print(out)
            
        except IndexError:
            return print('ERROR')

    def cwd(self, PORT = None, MYDIR = None):
        try:
            if PORT is None:
                PORT = self.port
            if MYDIR  is None:
                MYDIR = self.mydir
            # Sets workin directory
            # FILESYTEM:CWD <DIRPATH>
            #	i.e. FILESYSTEM:CWD "fd0:/LANG/LANG1"
            scope = self.gpibport(PORT)
            scope.write('FILESYSTEM:CWD "' + MYDIR + '"')
            
        except IndexError:
            return 0

    def mkdir(self, PORT = None, MYDIR = None):
        try:
            if PORT is None:
                PORT = self.port
            if MYDIR  is None:
                MYDIR = self.mydir
            # Creates Directory
            # FILESYSTEM:MKDIR "<DIRPATH>"
            #	i.e. FILESYSTEM:MKDIR "fd0:/LANG/LANG2"
            scope = self.gpibport(PORT)
            scope.write('FILESYSTEM:MKDIR "' + MYDIR + '"')
            
        except IndexError:
            return 0

    def rmdir(self, PORT = None, MYDIR = None):
        try:
            if PORT is None:
                PORT = self.port
            if MYDIR is None:
                MYDIR = self.mydir
            # Remove Directory
            #FILESYSTEM:RMDIR "<DIRPATH>"
            #	i.e. FILESYSTEM:RMDIR "fd0:/LANG/LANG2"
            scope = self.gpibport(PORT)
            scope.write('FILESYSTEM:RMDIR "' + MYDIR + '"')
            
        except IndexError:
            return 0
        
    def dirQ(self, PORT = None):
        try:
            if PORT is None:
                PORT = self.port
            # Queires FILES in Directory
            # FILESYSTEM:DIR?
            scope = self.gpibport(PORT)
            out = scope.query('FILESYSTEM:DIR?')
            print(out)
            
        except IndexError:
            return 0
            
    def changegpibport(self, PORT):
        try:
            # opens declared resource
            self.gpib = rm.open_resource(PORT)
            
        except IndexError:
            return ('No Input for Change')
        
    def changemydir(self, MYDIR):
        try:
            # redefines mydir
            self.mydir = MYDIR
            
        except IndexError:
            return print('No Input for Change')

    def changemyfile(self, MYFILE):
        try:
            # redefines myfile
            self.myfile = MYFILE
            
        except IndexError:
            return print('No Input for Change')

    def changechannel(self, CHANNEL):
        try:
            # redefines channel
            self.channel = CHANNEL
            
        except IndexError:
            return print('No Input for Change')

    def acquire(self, CHANNEL = None, PORT = None):
        try:
            if PORT is None:
                PORT = self.port
            if CHANNEL is None:
                CHANNEL = self.channel
            import pstl_getwaveform as getwfm 
            self.wave = getwfm.TDS640a(CHANNEL, PORT)

        except IndexError:
            return print('ERROR in Acquire')

    def saveplt(self, TITLE = None, xlabel = None, ylabel = None):
        try:
            wave = self.wave
            if TITLE is None:
                TITLE = wave.title
                title = "%s" % (TITLE)
            if xlabel is None:
                xlabel = "Time [%s]" % (wave.xunit)
            
            if ylabel is None:
                ylabel = "Voltage [%s]" % (wave.yunit)
            #
            import matplotlib.pyplot as plt
            # plot 
            fig = plt.figure(1, figsize=(6*3/2, 4*3/2))
            plt.clf()
            plt.plot(wave.time, wave.volts)
        
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            #plt.show()
            plt.savefig(self.mydir + wave.name + ".png")
            self.wave.fig = fig
            #plt.close(1)
        except IndexError:
            return 0

    def savewfm(self, MYDIR = None, MYFILE = None):
        try:
            if MYFILE is None:
                MYFILE = self.myfile
            if MYDIR is None:
                MYDIR = self.mydir
            h = self.wave
            aa = ('ymult', 'yzero', 'yoff', 'xincr', 'xdelay', 'volts', 'time', 'xunit',\
             'yunit', 'name', 'title', 'wfid', 'wfmpre')
            bb = (repr(h.ymult), repr(h.yzero), repr(h.yoff), repr(h.xincr), repr(h.xdelay),\
             repr(h.volts), repr(h.time), repr(h.xunit), repr(h.yunit),\
             repr(h.name), repr(h.title), repr(h.wfid), repr(h.wfmpre))

            file = open(MYDIR + MYFILE, "w")
            for a in range(1,len(aa)): 
                file.write(aa[a] + ' = ' + bb[a] + '\n')
            file.close
        except IndexError:
            return 0

    def getwfm(self, CHANNEL = None, PORT = None, TITLE = None, xlabel = None, ylabel = None,\
     MYDIR = None, MYFILE = None):
        try:
            self.acquire(CHANNEL, PORT)
            self.savewfm(MYDIR, MYFILE)
            self.saveplt(TITLE, xlabel, ylabel)
        except IndexError:
            return 0

    def enter(self):
        try:
            #import pyvisa as visa 
            # indicates which backend is being used
            rm = visa.ResourceManager()

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
            print('maybe change later with changegpibport(<newport>)')
            print('port = ' + port)

            print('\nSet Working Directory')
            print('i.e. For floppy fd0:/mydir/, input>> fd0:/mydir/')
            print('i.e. For windows computer C:\\User\\<youruser>\\Downloads\\, input>> ~\\Downloads\\')
            print('\t or input>> C:\\\\User\\\\<youruser>\\\\Downloads\\\\')
            print('maybe change later with changemydir(<newdir>)')
            mydir = input('mydir =\n>>')
            if '~\\' in mydir:
                mydir = os.path.expanduser(mydir)
            print('mydir = ' + mydir)

            print('\nSet default save file')
            print('i.e. TEK0.WFM')
            print('maybe change later with changemyfile(<newfile>)')
            myfile = input('myfile =\n>>')
            print('myfile = ' + myfile)

            print('\nSet default Channel, Math, or Reference')
            print('i.e. CH2, MATH1, REF3')
            print('maybe change later with changechannel(<newchannel>)')
            channel = input('channel =\n>>')
            print('channel = ' + channel)

            self.gpib = rm.open_resource(port)
        
            self.port = port
            self.myfile = myfile
            self.mydir = mydir
            self.channel = channel

        except IndexError:
            return 0
