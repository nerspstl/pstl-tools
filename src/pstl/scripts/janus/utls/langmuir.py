import numpy as np

def langmuir_calc_ps_grnd(vps,vr,r):
    current = np.divide(vr,r)
    vprobe = np.subtract(vps,vr)
    return vprobe,current
