import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime
import math


class Subplot():
    def __init__(self,ax,*args,**kwargs):
        self.ax=ax
        self.x=[]
        self.y=[]

        self.start_time=kwargs.get('start_time',None)
        self.logx=kwargs.get('logx',False)
        self.logy=kwargs.get('logy',False)
        self.xlimit_style=kwargs.get('xlimit_style',None)
        self.xlimit=kwargs.get('xlimit',None)
        self.ylimit_style=kwargs.get('ylimit_style',None)
        self.ylimit=kwargs.get('ylimit',None)


        self.func=kwargs.get('func',None)
        self.fargs=kwargs.get('fargs',None)

        self.location=kwargs.get('location',None)
        self.xlabel=kwargs.get('xlabel',None)
        self.ylabel=kwargs.get('ylabel',None)
        self.title=kwargs.get('title',None)

class Monitor():
    def __init__(self,nrows:int=1,ncols:int=1,**kwargs):
        self.nrows=nrows
        self.ncols=ncols

        self.alerts=kwargs.get('alerts',False)
        self.full_screen=kwargs.get('full_screen',False)

        fig,ax_list=\
                plt.subplots(nrows=nrows,ncols=ncols)
        self.figure=fig

        if nrows==1 and ncols==1:
            ax=[ax_list]
            nax=1
        else:
            ax=ax_list.ravel()
            nax=len(ax)
        self.axes=ax

        self.nax=nax
        subplot=[None]*nax
        for k in range(nax):
            subplot[k]=Subplot(ax[k],**kwargs)
        self.subplot=subplot

    # This function is called periodically from FuncAnimation
    def _animate(self, i):

        for k in range(self.nax):
            # set xs,ys
            xs=self.subplot[k].x
            ys=self.subplot[k].y

            # axes to use
            ax=self.axes[k]

            # Read temperature 
            if self.subplot[k].fargs is not None:
                y_out,self.subplot[k].fargs = \
                    self.subplot[k].func(self.subplot[k].fargs)
            else:
                y_out=self.sublpot[k].func()
            if self.subplot[k].start_time is True:
                x_out=datetime.datetime.now()
                self.subplot[k].start_time=x_out
            elif self.subplot[k].start_time is None:
                x_out=datetime.datetime.now()
            else:
                x_out=datetime.datetime.now()-self.subplot[k].start_time

            #roundoff museconds

            try:
                x_out=x_out.strftime('%H:%M:%S.%f')
            except:
                x_out=str(x_out-datetime.timedelta(microseconds=x_out.microseconds))


            # Add x and y to lists
            xs.append(x_out)
            ys.append(y_out)

            # Limit x and y lists to 20 items
            xs = xs[-20:]
            ys = ys[-20:]

            # Draw x and y lists
            ax.clear()
            if self.subplot[k].logx and self.subplot[k].logy:
                ax.loglog(xs, ys,\
                    marker='o',linestyle='-',markerfacecolor='none')
            elif self.subplot[k].logx:
                ax.semilogx(xs, ys,\
                    marker='o',linestyle='-',markerfacecolor='none')
            elif self.subplot[k].logy:
                ax.semilogy(xs, ys,\
                    marker='o',linestyle='-',markerfacecolor='none')
            else:
                ax.plot(xs, ys,\
                    marker='o',linestyle='-',markerfacecolor='none')

            self.subplot[k].x=xs
            self.subplot[k].y=ys

            # Format plot
            ax.grid(True)
            ax.tick_params(axis='x',labelrotation=45)
            #ax.set_xticklabls(ax.get_xticks(),rotation=45)
            ax.set(title=self.subplot[k].title)
            ax.set(xlabel=self.subplot[k].xlabel)
            ax.set(ylabel=self.subplot[k].ylabel)
            if self.subplot[k].ylimit_style == 'magnitude' or\
                    self.subplot[k].ylimit_style == 'm':
                        if self.subplot[k].ylimit is not None:
                            y_max=max(ys);y_min=min(ys)
                            magnitude_max=math.floor(math.log(y_max,10))
                            magnitude_min=math.floor(math.log(y_min,10))
                            #if self.subplot[k].ylimit is list\
                            #        and len(self.subplot[k].ylimit)==2:
                            if len(self.subplot[k].ylimit)==2:
                                        ylimit_max=math.pow(10,
                                                magnitude_max+\
                                                self.subplot[k].ylimit[1]
                                                )
                                        ylimit_min=math.pow(10,
                                                magnitude_min+\
                                                self.subplot[k].ylimit[0]
                                                )
                            elif self.subplot[k].ylimit is list\
                                    and len(self.subplot[k].ylimit)==1:
                                        ylimit_max=math.pow(10,
                                                magnitude_max+\
                                                self.subplot[k].ylimit[0]
                                                )
                                        ylimit_min=math.pow(10,
                                                magnitude_min-\
                                                self.subplot[k].ylimit[0])
                            elif self.subplot[k].ylimit is int\
                                    or self.subplot[k].ylimit is float:
                                        ylimit_max=math.pow(10,
                                                magnitude_max+\
                                                self.subplot[k].ylimit
                                                )
                                        ylimit_min=math.pow(10,
                                                magnitude_min-\
                                                self.subplot[k].ylimit)
                            else:
                                error_msg="\nERROR: '%s' is not a list, float or int\nit is a %s"%(str(self.subplot[k].ylimit),str(type(self.subplot[k].ylimit))) 
                                print(error_msg)
                            ax.set(ylim=[ylimit_min,ylimit_max])

                            

    def monitor(self,interval:float=1000):
        
        # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(self.figure, \
                self._animate, fargs=None, \
                interval=interval)
        wm = plt.get_current_fig_manager()
        if self.full_screen:
            wm.window.state('zoomed')
        plt.show()



