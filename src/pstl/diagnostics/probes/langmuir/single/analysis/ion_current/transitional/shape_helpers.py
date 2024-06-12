import numpy as np

from pstl.utls import constants as c
from pstl.diagnostics.probes.langmuir.single.analysis.ion_current.thin.shape_func_helpers import _function

# Functions for calculating current
def cylinderical_ab_calculator(r_p, lambda_De):
    ratio = r_p/lambda_De
    a = 1.18 - 0.00080*np.power(ratio, 1.35)
    b = 0.0684 + np.power(0.722+0.928*ratio, -0.729)
    return a, b

def cylinderical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_De):
    a,b = cylinderical_ab_calculator(r_p, lambda_De)
    return _partial_function(voltage, area, n0, V_s, m_i, KT_e, a, b)

def spherical_ab_calculator(r_p,lambda_De):
    ratio = r_p/lambda_De
    a = 1.58 + np.power(-0.056 + 0.816*ratio, -0.744)
    b = -0.933 + np.power(0.0148+0.119*ratio, -0.125)
    return a, b

def spherical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_De):
    a, b =spherical_ab_calculator(r_p, lambda_De)
    return _partial_function(voltage, area, n0, V_s, m_i, KT_e, a, b)

def planar_ab_calculator(r_p,lambda_De):
    ratio = r_p/lambda_De
    a = np.exp(-0.5)*np.sqrt(2*np.pi)*(2.28*np.power(ratio, -0.749))
    b = 0.806*np.power(ratio, -0.0692)
    return a, b

def planar_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_De):
    a, b = planar_ab_calculator(r_p, lambda_De)
    partial = _partial_function(voltage, area, n0, V_s, m_i, KT_e, a, b)
    standard = _function(area, n0, m_i, KT_e)
    return np.add(partial, standard)


# Functions for calculating current (position arguments important for wrappers here) #######
def wrapper_cylinderical_function(voltage, V_s, KT_e, area, n0, m_i, r_p, lambda_De):
    return cylinderical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_De)


def wrapper_spherical_function(voltage, V_s, KT_e, area, n0, m_i, r_p, lambda_De):
    return spherical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_De)


def wrapper_planar_function(voltage, V_s, KT_e, area, n0, m_i, r_p, lambda_De):
    return planar_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_De)
#############################################################################################


# generalized
def _partial_function(voltage, area, n0, V_s, m_i, KT_e, a, b):
    A = (c.e*n0*area)*np.sqrt(c.e*KT_e/(2*np.pi*m_i))*a

    x = np.divide(V_s-voltage, KT_e)

    with np.errstate(invalid="ignore"):
        power_x = np.power(x, b)

    current = np.multiply(
        A,
        power_x
    )

    return current
