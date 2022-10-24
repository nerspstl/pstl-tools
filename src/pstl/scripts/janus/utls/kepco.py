import numpy as np


# some functions are dependent on classes defined elsewhere
# here they are passed in and functions are called


def offVoltage(ps):
    ps.setVoltage(0)


def setupSupplyVoltages():
    vstart=-1
    vstop=1
    dv=1
    return np.arange(vstart,vstop+dv,dv)


