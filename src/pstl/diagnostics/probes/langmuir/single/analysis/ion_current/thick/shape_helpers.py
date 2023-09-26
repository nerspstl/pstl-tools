import numpy as np

from pstl.utls import constants as c
###############################################################################
# Functions for calculating current (position arguments important for wrappers here) #######
# make these more robust by changing position arguments to keyword arguments via dictionary
def wrapper_cylinderical_function(voltage, V_s, KT_e, area, n0, m_i):
    """
    Wrapper designed to elimeate the KT_e variable from passing to the
    call to the cylinderical function
    """
    return cylinderical_function(voltage, area, n0, V_s, m_i)

def wrapper_spherical_function(voltage, V_s, KT_e, area, n0, m_i):
    return spherical_function(voltage, area, n0, V_s, m_i, KT_e)


def wrapper_planar_function(voltage, V_s, KT_e, area, n0, m_i):
    return planar_function(voltage, area, n0, V_s, m_i, KT_e)
###############################################################################

###############################################################################
# Solves for currents #########################################################
def cylinderical_function(voltage, area, n0, V_s, m_i):
    A = (c.e*n0*area/np.pi)*np.sqrt(2*c.e/m_i)

    with np.errstate(invalid="ignore"):
        sqrt_x = np.sqrt(V_s-voltage)

    current = -np.multiply(
        A,
        sqrt_x
    )

    return current


def spherical_function(voltage, area, n0, V_s, m_i, KT_e):
    return _spherical_and_planar_function(voltage, area, n0, V_s, m_i, KT_e)


def planar_function(voltage, area, n0, V_s, m_i, KT_e):
    return _spherical_and_planar_function(voltage, area, n0, V_s, m_i, KT_e)
###############################################################################


###############################################################################
# Spherical and Planar (generalized to one function) ##########################
def _spherical_and_planar_function(voltage, area, n0, V_s, m_i, KT_e):
    A = (c.e*n0*area)*np.sqrt(c.e*KT_e/(2*np.pi*m_i))

    current = -np.multiply(A, np.divide(V_s-voltage, KT_e))

    return current
###############################################################################
