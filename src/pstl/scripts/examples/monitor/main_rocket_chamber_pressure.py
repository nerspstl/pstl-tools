import datetime
import time 
import atexit
from contextlib import redirect_stdout
import os
import inspect

import serial
import numpy as np

from pstl.tools.alerts import logs
from pstl.tools.alerts import center
from pstl.tools.alerts import monitor


def warning_send(s,attempt:str=None):
    Sender=center.sender('pstlrc','mynotifier')
    now = datetime.datetime.now()
    now_date=now.strftime("%b-%d-%Y")
    
    subject="Pressure Warning: "+now_date+attempt
    body=s
    msgtype="warning"

    groupname='rocket'

    center.contact_group(Sender,body,groupname,'all',subject=subject)

def update_send(s):
    Sender=center.sender('pstlrc','mynotifier')
    now = datetime.datetime.now()
    now_date=now.strftime("%b-%d-%Y")
    
    subject="Pressure Update: "+now_date
    body=s
    msgtype="info"

    groupname='rocket'

    center.contact_group(Sender,body,groupname,'email',subject=subject)

def gas_correction(gas,logname):
    gas=gas.upper()
    if gas == "air".upper():
        gcf=1
    elif gas == "n2".upper():
        gcf=1
    elif gas == "xe".upper():
        gcf=0.4
    else:
        sout=("%s is not a known gas\nUsing gcf=1.0\n"%(gas))
        print(sout)
        loggit(logname,sout)
        gcf=1.0

    return gcf


def bpg402_torr(hv,lv,gas="N2",logname=None):
    e=np.divide((np.multiply(hv,256)+lv),4000)-12.625
    p=np.power(10,e)
    if gas != "N2".upper() or gas != "air".upper():
        gcf=gas_correction(gas,logname)
        p=p*gcf
    return p

def find75(o):
    i7=[i7 for i7,x in enumerate(o) if x==7]
    i5=[i5 for i5,x in enumerate(o) if x==5]
    print(i7)
    print(i5)
    if len(i7)==1 and len(i5)==1:
        print("pass")
        out=o[i7[0]:]+o[:i7[0]]
        if i7[0]+1==i5[0]:
            ihv=int(i7[0]+4)
            ilv=int(i7[0]+5)
    else:
        print("fail")
                
    return out,ihv,ilv

def calculate(ser,gas="N2",resetmax=5,logname=None):
    gas=gas.upper()
    reset=0
    RESET=[]
    collect=True
    while collect:
        if reset<resetmax:
            out=get_bytes(ser)
            if out is str:
                print(out)
                error=out
            else:
                error=out[3]
            if error==0:
                collect=False
                # collect
                hv=out[4];lv=out[5]
                p=bpg402_torr(hv,lv,gas=gas,logname=logname)
            else:
                reset = reset+1
                RESET.append(out)
        else:
            now = datetime.datetime.now()
            now_date=now.strftime("%b-%d-%Y")
            now = now.strftime("%b-%d-%Y %H:%M:%S")
            p="Error: @ %s had %i resets in a row\n%s\n"%(now,resetmax,str(RESET))
            collect=False
    return p,reset,out

def check(p,pressureLimit,gas="N2"):
    if p>pressureLimit:
        ok=False
    else:
        ok=True
    return ok

def get_bytes(ser):
    o=list(ser.read(9))
    I7=[i7 for i7,x in enumerate(o) if x==7]
    I5=[i5 for i5,x in enumerate(o) if x==5]
    if I7 != []  and I5 != []:
        for k in I7:
            for z in I5:
                if k+1==z:
                    i7=k
                    i5=z
                    out=o[i7:]+o[:i7]
                elif k+1==9 and z==0:
                    i7=k
                    i5=z
                    out=o[i7:]+o[:i7]
                else:
                    now = datetime.datetime.now()
                    now_date=now.strftime("%b-%d-%Y")
                    now = now.strftime("%b-%d-%Y %H:%M:%S")
                    out="Error: @ %s could not find 7, 5 in correct order\n%s\n"%(now,str(o))
    else:
        now = datetime.datetime.now()
        now_date=now.strftime("%b-%d-%Y")
        now = now.strftime("%b-%d-%Y %H:%M:%S")
        out="Error: @ %s could not find 7, 5 in correct order\n%s\n"%(now,str(o))

    return out


def exit_handler(LogicReset,logfile):
        if LogicReset==0:
            pass
            sout=("Info: No Logic Resets")
        else:
            sout=("Info: Number of Logic Resets %i"%(LogicReset))
        print(sout)
        loggit(logfile,sout)
    
def setup_loggit(filename:str=None):

    now = datetime.datetime.now()
    now_date=now.strftime("%Y_%m_%d_%H_%M_%S")
    if filename is None:
        frame=inspect.stack()[1]
        module=inspect.getmodule(frame[0])
        filename=os.path.splitext(os.path.basename(frame.filename))[0]
        filename=('out_'+filename+'_'
                +now_date+'.txt')
    logs_path=inspect.getfile(logs)
    logs_path=os.path.dirname(logs_path)
    full_file_location=os.path.join(logs_path,filename)
    print("Log file saved to:\n%s\n"%(full_file_location))
    return full_file_location

def loggit(filename:str,output):
    with open(filename,'a') as f:
        f.write(output)
class Args():
    def __init__(self,*args):
        self.args=args
    def update(self,*args):
        self.args=args

def loop(args):
    (logname,now_start,loggit,repeatSend,firstSend,
        send,sendUpdate,delay_update,repeat_1,
        delay_1,repeat_2,delay_2,now_last_send,now_last_update,
        logicReset,pressureLimit,gas,ser)=args

    p,reset,out=calculate(ser,gas=gas,logname=logname)
    if reset != 0:
        logicReset=logicReset + 1
    if p is str:
        ok=False
        s=p
    else:
        ok=check(p,pressureLimit,gas=gas)
        if ok:
            now = datetime.datetime.now()
            now_date=now.strftime("%b-%d-%Y")
            now = now.strftime("%b-%d-%Y %H:%M:%S")
            s="Update: @ %s Pressure=%.3e torr using %s\nBytes: %s\n"%(now,p,gas,str(out))
        else:
            now = datetime.datetime.now()
            now_date=now.strftime("%b-%d-%Y")
            now = now.strftime("%b-%d-%Y %H:%M:%S")
            s="Warning: @ %s Pressure=%.3e torr using %s\nBytes: %s\n"%(now,p,gas,str(out))


    if ok:
        pass
    else:
        loggit(logname,s)
        print(s)
        attempt=None

        if now_last_send is None:
            now_last_send=time.time()

        if firstSend:
            sout='Sending First Notification\n'
            loggit(logname,sout)
            print(sout)
            attempt=' (First Attempt)'
            firstSend=False
        elif repeatSend:
            if repeat_1:
                if time.time()-now_last_send >= delay_1:
                    sout='Sending Second Notification\n'
                    loggit(logname,sout)
                    print(sout)
                    attempt=' (Second Attempt)'
                    send=True
                    repeat_1=False
                else:
                    send=False
            else:
                if repeat_2:
                    if time.time()-now_last_send >= delay_2:
                        sout='Sending Third Notification\n'
                        loggit(logname,sout)
                        print(sout)
                        attempt=' (Third Attempt)'
                        send=True
                        repeat_2=False
                    else:
                        send=False
        else:
            send=False

        if send:
            warning_send(s,attempt)
            send=False
        elif sendUpdate:
            if now_last_update is None:
                now_last_update=time.time()
            if time.time()-now_last_update >= delay_update:
                sout="Sending Update\n"
                print(sout)
                update_send(s)
                now_last_update=time.time()
        else:
            pass

    fargs=(logname,now_start,loggit,repeatSend,
            firstSend,send,sendUpdate,
            delay_update,repeat_1,delay_1,repeat_2,delay_2,
            now_last_send,now_last_update,
            logicReset,pressureLimit,gas,ser)

    return p,fargs


def main():
    logname=setup_loggit()
    now=datetime.datetime.now()
    now_start=now.strftime("%b-%d-%Y %H:%M:%S")
    loggit(logname,'Start of %s\n'%(now_start))
    repeatSend=True
    firstSend=True
    send=True
    sendUpdate=True
    delay_update=3600
    now_last_update=None
    repeat_1=True
    delay_1=20
    repeat_2=True
    delay_2=60
    now_last_send=None
    logicReset=0
    pressureLimit=1e-3
    gas="n2"
    ser=serial.Serial("COM1")
    # first grab is iffy
    # so ignore it
    out=get_bytes(ser)
    fargs=(logname,now_start,loggit,repeatSend,firstSend,send,sendUpdate,
            delay_update,repeat_1,delay_1,repeat_2,delay_2,now_last_send,
            now_last_update,logicReset,pressureLimit,gas,ser)
    inficon_pressure=monitor.Monitor(1,1,\
            xlabel='time [s]',ylabel='pressure [torr]',\
            title='Inficon BPG402S Pressure',alerts=False,\
            func=loop,fargs=(fargs),start_time=True,\
            ylimit_style='m',ylimit=[-1,1],logy=False
            )
    print("running ...")
    try:
        inficon_pressure.monitor()
    except KeyboardInterrupt:
        loggit(logname,'End of %s\n'%(now_start))
        print("exiting ...")
    exit_handler(logicReset,logname)


if __name__ == "__main__":
    main()
