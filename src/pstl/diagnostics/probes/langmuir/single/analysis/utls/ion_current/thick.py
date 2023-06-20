import numpy as np

from pstl.utls import constants as c
from pstl.utls.helpers import method_function_combiner
from pstl.utls.helpers import method_selector as method_selector
from pstl.utls.helpers import FunctionFit, CustomFit, make_CustomFit
from pstl.utls.decorators import where_function_else_zero


def shape_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_methods, available_functions)
    return func


def cylinderical_method(voltage, area, n0, V_s, m_i, KT_e, *args, **kwargs):

    func = where_function_else_zero(
        _cylinderical_function, cylinderical_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "thick", "shape": "cylinderical", "fit": fit}
    return I_i, extras


def spherical_method(voltage, area, n0, V_s, m_i, KT_e, *args, **kwargs):
    func = where_function_else_zero(
        _spherical_function, spherical_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "thick", "shape": "spherical", "fit": fit}
    return I_i, extras


def planar_method(voltage, area, n0, V_s, m_i, KT_e, *args, **kwargs):

    func = where_function_else_zero(
        _planar_function, planar_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "thick", "shape": "planar", "fit": fit}
    return I_i, extras


# domain conditions
def cylinderical_domain_condition(voltage, V_s, KT_e):
    return _domain_condition(voltage, V_s, KT_e)


def spherical_domain_condition(voltage, V_s, KT_e):
    return _domain_condition(voltage, V_s, KT_e)


def planar_domain_condition(voltage, V_s, KT_e):
    return _domain_condition(voltage, V_s, KT_e)

# generalized domain


def _domain_condition(voltage, V_s, KT_e):
    condition = np.divide(
        np.subtract(V_s, voltage),  # [V]
        KT_e                         # [eV]
    )
    return condition > 1  # >>1


# Functions for calculating current (position arguments important for wrappers here) #######
# make these more robust by changing position arguments to keyword arguments via dictionary
def _cylinderical_function(voltage, V_s, KT_e, area, n0, m_i):
    return cylinderical_function(voltage, area, n0, V_s, m_i)


def _spherical_function(voltage, V_s, KT_e, area, n0, m_i):
    return spherical_function(voltage, area, n0, V_s, m_i, KT_e)


def _planar_function(voltage, V_s, KT_e, area, n0, m_i):
    return planar_function(voltage, area, n0, V_s, m_i, KT_e)
#############################################################################################


def cylinderical_function(voltage, area, n0, V_s, m_i):
    A = (c.e*n0*area/np.pi)*np.sqrt(2*c.e/m_i)

    with np.errstate(invalid="ignore"):
        sqrt_x = np.sqrt(V_s-voltage)

    current = np.multiply(
        A,
        sqrt_x
    )

    return current


def spherical_function(voltage, area, n0, V_s, m_i, KT_e):
    return _spherical_and_planar_function(voltage, area, n0, V_s, m_i, KT_e)


def planar_function(voltage, area, n0, V_s, m_i, KT_e):
    return _spherical_and_planar_function(voltage, area, n0, V_s, m_i, KT_e)

# generalized


def _spherical_and_planar_function(voltage, area, n0, V_s, m_i, KT_e):
    A = (c.e*n0*area)*np.sqrt(c.e*KT_e/(2*np.pi*m_i))

    current = np.multiply(A, np.divide(V_s-voltage, KT_e))

    return current


# Declare available methods
available_methods = {
    0: ['cylinderical'],
    1: ['spherical'],
    2: ['planar', 'planer'],
}
# Declare correspondin functions for available_methods
available_functions = {
    0: cylinderical_method,
    1: spherical_method,
    2: planar_method,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
options = method_function_combiner(available_methods, available_functions)
