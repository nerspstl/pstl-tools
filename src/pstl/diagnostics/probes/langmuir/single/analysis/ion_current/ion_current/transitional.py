import numpy as np

from pstl.diagnostics.probes.langmuir.single.analysis.utls.ion_current.thin import _function
from pstl.utls import constants as c
from pstl.utls.decorators import where_function_else_zero
from pstl.utls.helpers import method_function_combiner
from pstl.utls.helpers import method_selector as method_selector
from pstl.utls.helpers import make_CustomFit


def shape_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_methods, available_functions)
    return func


def cylinderical_method(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D, *args, **kwargs):

    func = where_function_else_zero(
        _cylinderical_function, cylinderical_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i, r_p, lambda_D)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "transitional", "shape": "cylinderical", "fit": fit}
    return I_i, extras


def spherical_method(voltage, area, n0, V_s, m_i, KT_e,  r_p, lambda_D, *args, **kwargs):
    func = where_function_else_zero(
        _spherical_function, spherical_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i, r_p, lambda_D)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "transitional", "shape": "spherical", "fit": fit}
    return I_i, extras


def planar_method(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D, *args, **kwargs):
    func = where_function_else_zero(
        _planar_function, planar_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i, r_p, lambda_D)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "transitional", "shape": "planar", "fit": fit}
    return I_i, extras


# domain conditions
def cylinderical_domain_condition(voltage, V_s, KT_e):
    return _cylinderical_spherical_domain_condition(voltage, V_s, KT_e)


def spherical_domain_condition(voltage, V_s, KT_e):
    return _cylinderical_spherical_domain_condition(voltage, V_s, KT_e)


def planar_domain_condition(voltage, V_s, KT_e):
    condition = np.divide(
        np.subtract(V_s, voltage),  # [V]
        KT_e                         # [eV]
    )

    returns = np.where

    cond1 = 3 < condition
    cond2 = condition < 30
    return np.logical_and(cond1, cond2)  # 10 < rp/l < 45

# generalized domain


def _cylinderical_spherical_domain_condition(voltage, V_s, KT_e):
    condition = np.divide(
        np.subtract(V_s, voltage),  # [V]
        KT_e                         # [eV]
    )
    return condition > 1


# Functions for calculating current
def cylinderical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D):
    ratio = r_p/lambda_D
    a = 1.18 - 0.00080*np.power(ratio, 1.35)
    b = 0.0684 + np.power(0.722+0.928*ratio, -0.729)
    return _partial_function(voltage, area, n0, V_s, m_i, KT_e, a, b)


def spherical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D):
    ratio = r_p/lambda_D
    a = 1.58 + np.power(-0.056 + 0.816*ratio, -0.744)
    b = -0.933 + np.power(0.0148+0.119*ratio, -0.125)
    return _partial_function(voltage, area, n0, V_s, m_i, KT_e, a, b)


def planar_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D):
    ratio = r_p/lambda_D
    a = np.exp(-0.5)*np.sqrt(2*np.pi)*(2.28*np.power(ratio, -0.749))
    b = 0.806*np.power(ratio, -0.0692)
    partial = _partial_function(voltage, area, n0, V_s, m_i, KT_e, a, b)
    standard = _function(area, n0, m_i, KT_e)
    return np.add(partial, standard)


# Functions for calculating current (position arguments important for wrappers here) #######
def _cylinderical_function(voltage, V_s, KT_e, area, n0, m_i, r_p, lambda_D):
    return cylinderical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D)


def _spherical_function(voltage, V_s, KT_e, area, n0, m_i, r_p, lambda_D):
    return spherical_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D)


def _planar_function(voltage, V_s, KT_e, area, n0, m_i, r_p, lambda_D):
    return planar_function(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D)
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
