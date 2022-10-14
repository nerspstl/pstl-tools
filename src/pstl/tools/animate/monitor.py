import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import datetime
import math


class Subplot():
    def __init__(self,ax,*args,**kwargs):
        # assign axes for figure
        self.ax=ax

        # Data list for what to plot are intialized
        self.x=[]
        self.y=[]

        # Start_time for data collection with x-axis in time
        # True: get start time (starts at 0)
        # False: Dont do time as x-axis
        # None: Actually time for each data point
        # Anything else: if in proper datetime format will be start time
        self.start_time=kwargs.get('start_time',True)

        # True if log scale
        self.logx=kwargs.get('logx',False)
        self.logy=kwargs.get('logy',False)

        # plotting kwargs
        plot_kwargs_defaults={
                'marker':'o',
                'linestyle':'-',
                'markerfacecolor':'none'
                }
        self.plot_kwargs=kwargs.get('plot_kwargs',plot_kwargs_defaults)

        # limit_style is either 'magnitude' or None
        # currently limits on x-axis are not yet implemented
        # only ylimit magnitude is implemented
        # magnitude sets how many magnitudes above current magnitude
        # i.e. currentmax  is 4, then magnitude above upper limit would be 10
        self.xlimit_style=kwargs.get('xlimit_style',None)
        self.xlimit=kwargs.get('xlimit',None)
        self.ylimit_style=kwargs.get('ylimit_style',None)
        self.ylimit=kwargs.get('ylimit',None)

        # restrict number of plotted from a list
        self.updatelimit=kwargs.get('updatelimit',None)

        # True to show an update line
        # for updateline_kwargs must be a dictionary
        self.updateline=kwargs.get('updateline',False)
        self.updateline_kwargs=kwargs.get('updateline_kwargs',None)

        # function and function_arguments to get updated x,y for
        self.func=kwargs.get('func',None)
        self.fargs=kwargs.get('fargs',None)

        self.location=kwargs.get('location',None) # not sure why here??

        # plot stuff
        self.grid=kwargs.get('grid',True)
        self.xlabel=kwargs.get('xlabel',None)
        self.ylabel=kwargs.get('ylabel',None)
        self.title=kwargs.get('title',None)

class Figure():
    def __init__(self,nrows:int=1,ncols:int=1,**kwargs):
        # for figure subplot, determins how many rows and cols
        self.nrows=kwargs.get('nrows',nrows)
        self.ncols=kwargs.get('ncols',ncols)

        # if alerts will be used (not yet implemented)
        self.alerts=kwargs.get('alerts',False)

        # Make full screen (true)
        self.full_screen=kwargs.get('full_screen',False)

        # Creates the fig and axes
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
        
        # number of axes
        self.nax=nax
        # initialize list of subplots
        subplot=[None]*nax
        for k in range(nax):
            subplot[k]=Subplot(ax[k],**kwargs)
        self.subplot=subplot

    ## This function is called periodically from FuncAnimation
    def _animate(self, i):

        for k in range(self.nax):
            # rename self.subplot for easy
            subplot=self.subplot[k]

            # set xs,ys
            xs=subplot.x
            ys=subplot.y

            # axes to use
            ax=self.axes[k]

            # get data from frunction
            # if,else if fargs need to be passed in
            if subplot.fargs is not None:
                y_out,subplot.fargs = \
                    subplot.func(subplot.fargs)
            else:
                y_out=subplot.func()

            # If x-axis is time
            if subplot.start_time is not False:
                if subplot.start_time is True:
                    x_out=datetime.datetime.now()
                    subplot.start_time=x_out
                    x_out=x_out-subplot.start_time
                elif subplot.start_time is None:
                    x_out=datetime.datetime.now()
                else:
                    x_out=datetime.datetime.now()-subplot.start_time

                # round-off museconds
                try:
                    x_out=x_out.strftime('%H:%M:%S.%f')
                except:
                    x_out=str(x_out-datetime.timedelta(
                        microseconds=x_out.microseconds)
                        )
            else: # False (no time dependence)
            # if FAlSE then 
            # no time and x_out will come from either data or index
                pass



            # Add x and y to lists
            xs.append(x_out)
            ys.append(y_out)

            # Restricts x and y lists to last 20 items
            if subplot.updatelimit is not None:
                xs = xs[-int(subplot.updatelimit):]
                ys = ys[-int(subplot.updatelimit):]
            else:
                pass

            # Plot x and y lists (logscale if true)
            ax.clear()
            if subplot.logx and subplot.logy:   # loglog
                ax.loglog(xs, ys,**subplot.plot_kwargs)
            elif subplot.logx:                  # semilogx
                ax.semilogx(xs, ys,**subplot.plot_kwargs)
            elif subplot.logy:                  # semilogy
                ax.semilogy(xs, ys,**subplot.plot_kwargs)
            else:                               # linear plot
                ax.plot(xs, ys,**subplot.plot_kwargs)

            # Plot update line if true
            if subplot.updateline and subplot.updateline_kwargs is not None:
                ax.axvline(xs[-1],**subplot.updateline_kwargs)
            elif subplot.updateline:
                ax.axvline(xs[-1],color='r')
            else:
                pass

            # Update the class x,y with the new xs,ys
            subplot.x=xs
            subplot.y=ys

            # Format plot
            ax.grid(subplot.grid)
            ax.tick_params(axis='x',labelrotation=45)
            #ax.set_xticklabls(ax.get_xticks(),rotation=45)
            ax.set(title=subplot.title)
            ax.set(xlabel=subplot.xlabel)
            ax.set(ylabel=subplot.ylabel)
            if subplot.ylimit_style == 'magnitude' or\
                    subplot.ylimit_style == 'm':
                        if subplot.ylimit is not None:
                            y_max=max(ys);y_min=min(ys)
                            magnitude_max=math.floor(math.log(y_max,10))
                            magnitude_min=math.floor(math.log(y_min,10))
                            #if self.subplot[k].ylimit is list\
                            #        and len(self.subplot[k].ylimit)==2:
                            if len(subplot.ylimit)==2:
                                        ylimit_max=math.pow(10,
                                                magnitude_max+\
                                                subplot.ylimit[1]
                                                )
                                        ylimit_min=math.pow(10,
                                                magnitude_min+\
                                                subplot.ylimit[0]
                                                )
                            elif subplot.ylimit is list\
                                    and len(subplot.ylimit)==1:
                                        ylimit_max=math.pow(10,
                                                magnitude_max+\
                                                subplot.ylimit[0]
                                                )
                                        ylimit_min=math.pow(10,
                                                magnitude_min-\
                                                subplot.ylimit[0])
                            elif subplot.ylimit is int\
                                    or subplot.ylimit is float:
                                        ylimit_max=math.pow(10,
                                                magnitude_max+\
                                                subplot.ylimit
                                                )
                                        ylimit_min=math.pow(10,
                                                magnitude_min-\
                                                subplot.ylimit)
                            else:
                                error_msg="\nERROR: '%s' is not a list, float or int\nit is a %s"%(str(subplot.ylimit),str(type(subplot.ylimit))) 
                                print(error_msg)
                            ax.set(ylim=[ylimit_min,ylimit_max])
                            
    ## Callable function that animates the plot and calls _animate
    def monitor(self,**kwargs):
        """
        kwargs: see matplotlib.animation.FuncAnimation
        defaults built into this class include:
        fig=self.figure (from this Figure class)
        func=self._animate (from this Figure class)
            THIS IS NOT the updating data function
            That is seperatly called inside the self._animate
            func from the Subplot class
        fargs=None as nothing else is passed to self._animate
            as the self._animate function calls its own function
            and fargs for data collection from the Subplot class
        """
        # set defaults in kwargs
        fig=kwargs.pop('fig',self.figure)
        func=kwargs.pop('func',self._animate)
        kwargs['fargs']=kwargs.get('fargs',None)
        # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(fig,func,**kwargs)
        # to do full screen
        wm = plt.get_current_fig_manager()
        if self.full_screen:
            wm.window.state('zoomed')
        # update & show plot
        plt.show()



