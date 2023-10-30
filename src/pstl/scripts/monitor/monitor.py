import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime as dt
from pstl.instruments.daq.agilent.models import Agilent34970A as DAQ

class ALARM():
    def __init__(self,upper=130,lower=105):
        self.upper=upper
        self.lower=lower

class SUBPLOT():
    def __init__(self,ax,location=None):
        self.ax=ax
        self.location=location
        self.x=[]
        self.y=[]

        self.ylim=[95,135]
        self.alarm=ALARM()


class MONITOR():
    def __init__(self,nrows,ncols):
        self.nrows=nrows
        self.ncols=ncols

        fig,ax_list=plt.subplots(nrows=3,ncols=3)
        self.figure=fig

        ax=ax_list.ravel()
        self.axes=ax

        nax=len(ax)
        self.nax=nax
        subplot=[None]*nax
        r=[None]*nax
        for k in range(nax):
            subplot[k]=SUBPLOT(ax[k],int(112+k))
        self.subplot=subplot

        #daq=DAQ("GPIB0::10::INSTR")
        daq=DAQ()

        daq.addCardAgilent34901A(1,20,'TCK')


        self.daq=daq

    # This function is called periodically from FuncAnimation
    def animate(self, i):

        for k in range(self.nax):
            # handel
            dis=self.subplot[k]

            # set xs,ys
            xs=self.subplot[k].x
            ys=self.subplot[k].y

            # axes to use
            ax=self.axes[k]

            # Read temperature 
            temp_c = round(float(self.daq.get(self.subplot[k].location)),2)

            # Add x and y to lists
            xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
            ys.append(temp_c)

            # Limit x and y lists to 20 items
            xs = xs[-20:]
            ys = ys[-20:]

            # Draw x and y lists
            ax.clear()
            ax.plot(xs, ys,\
                marker='o',linestyle='-',markerfacecolor='none')

            # horizontal limit alarm
            ax.axhline(y=dis.alarm.upper,color='r')
            ax.axhline(y=dis.alarm.lower,color='r')

            self.subplot[k].x=xs
            self.subplot[k].y=ys

            # Format plot
            #ax.set_xticks(rotation=45, ha='right')
            ax.grid(True)
            ax.set_xticklabels([])
            #ax.set_xticks([])
            if ys[-1]>=dis.ylim[0] and ys[-1]<=dis.ylim[1]:
                ax.set(ylim=dis.ylim)
            #plt.subplots_adjust(bottom=0.30)
            ax.set(title='TEMP at %s'%(str(dis.location)))
            ax.set(xlabel='Time [s]')
            ax.set(ylabel='Temperature [deg C]')

    def monitor(self):
        
        # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(self.figure, self.animate, fargs=None, interval=1000)
        wm = plt.get_current_fig_manager()
        wm.window.state('zoomed')
        plt.show()


def monitor():
    temperatures=MONITOR(3,3)
    print("monitoring...")
    temperatures.monitor()



