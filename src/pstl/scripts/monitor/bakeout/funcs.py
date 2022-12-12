import numpy as np

def set_title_pressure(ax):
    line=ax.lines[0]
    ydata=line.get_ydata()
    
    # get last data point
    ylast=ydata[-1]

    title="Pressure is %.2e torr"%(ylast)

    ax.set(title=title)

def alert_temperature(ax,send_alarm=False,sent_alarms=0,repeat=3,
        delay=[20,60],start_time=True,recover=False):

