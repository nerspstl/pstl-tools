import matplotlib.pyplot as plt
import time
from pstl.instruments.daq.agilent.agilent34970A import AGILENT34970A as DAQ

class SUBPLOT():
    def __init__(self,ax,location=None):
        self.ax=ax
        self.location=location
        self.x=[]
        self.y=[]


class MONITOR():
    def __init__(self,nrows,ncols):
        self.nrows=nrows
        self.ncols=ncols

        fig,ax_list=plt.subplots(nrows=3,ncols=3)
        self.figure=fig
        ax=ax_list.ravel()
        self.axes=ax
        wm = plt.get_current_fig_manager()
        wm.window.state('zoomed')

        nax=len(ax)
        self.nax=nax
        subplot=[None]*nax
        r=[None]*nax
        for k in range(nax):
            subplot[k]=SUBPLOT(ax[k],int(113+k))
        self.subplot=subplot

        daq=DAQ()

        daq.addCardAgilent34901A(1,20,'TCK')


        self.daq=daq

    def monitor(self):
        r=[None]*self.nax
        dt=[None]*self.nax
        start_time = None
        while True:
            try:
                for k in range(self.nax):
                    dis=self.subplot[k]
                    # get time
                    t = time.time()
                    if start_time is None:
                        start_time = t
                    dis.x.append(\
                            t - start_time\
                            )
                    dis.y.append(\
                            float(self.daq.get(self.subplot[k].location))\
                            )
                    dis.ax.plot(dis.x,dis.y,"-b")
            except KeyboardInterrupt:
                print("Exitting loop..")
                break



def monitor():
    temperatures=MONITOR(3,3)
    temperatures.monitor()



