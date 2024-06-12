import numpy as np

from pstl.utls import constants as c

def _xs(voltage, V_s, KT_e, lambda_D):
    A = lambda_D*np.sqrt(2)/3
    x = 2*(V_s-voltage)/KT_e
    with np.errstate(invalid="ignore"):
        power_x = np.power(x, 0.75)
    return np.multiply(A, power_x)


def _function(area, n0, m_i, KT_e):
    return np.exp(-0.5)*c.e*n0*area*np.sqrt(c.e*KT_e/m_i)


def _constant_function(voltage, current, *args, **kwargs):
    return np.ones_like(voltage)*_function(*args)
