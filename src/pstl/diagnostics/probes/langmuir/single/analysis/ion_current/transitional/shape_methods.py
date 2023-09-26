import numpy as np

from pstl.utls import constants as c
from pstl.utls.decorators import where_function_else_zero
from pstl.utls.helpers import make_CustomFit

from .shape_helpers import (
    wrapper_cylinderical_function,
    wrapper_spherical_function,
    wrapper_planar_function,
)

from .shape_domains import (
    cylinderical_domain_condition,
    spherical_domain_condition,
    planar_domain_condition,
)



def cylinderical_method(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D, *args, **kwargs):

    func = where_function_else_zero(
        wrapper_cylinderical_function, cylinderical_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i, r_p, lambda_D)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "transitional", "shape": "cylinderical", "fit": fit}
    return I_i, extras


def spherical_method(voltage, area, n0, V_s, m_i, KT_e,  r_p, lambda_D, *args, **kwargs):
    func = where_function_else_zero(
        wrapper_spherical_function, spherical_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i, r_p, lambda_D)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "transitional", "shape": "spherical", "fit": fit}
    return I_i, extras


def planar_method(voltage, area, n0, V_s, m_i, KT_e, r_p, lambda_D, *args, **kwargs):
    func = where_function_else_zero(
        wrapper_planar_function, planar_domain_condition)

    coefs = (V_s, KT_e, area, n0, m_i, r_p, lambda_D)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "transitional", "shape": "planar", "fit": fit}
    return I_i, extras


