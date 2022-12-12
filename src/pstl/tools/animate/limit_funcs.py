import numpy as np

def between(ax,lower,upper,line_num=0,axes="y"):
    """
    Line data from the axes object is taken and the 
    axes (x or y) to set the limit
    """
    # retreive line data
    line=ax.lines[line_num]
    if axes=="y":
        data=line.get_ydata()
    elif axex=="x":
        data=line.get_xdata()
    else:
        raise ValueError("Keyword axes '%s' is not 'x' or 'y'"%(axes))

    # get max and min
    data_max = max(data)
    data_min = min(data)
   
    # set limit if surpass

    # if below limit
    if data_min>=lower and data_max<=upper:
        # set limit
        if axes=="y":
            ax.set(ylim=[lower,upper])
        elif axes=="x":
            ax.set(xlim=[lower,upper])
        else:
            raise ValueError("Keyword axes '%s' is not 'x' or 'y'"%(axes))

    

    
