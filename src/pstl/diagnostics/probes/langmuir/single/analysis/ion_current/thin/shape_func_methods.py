import numpy as np

from .shape_domains import (
    cylinderical_domain_condition,
    spherical_domain_condition,
    planar_domain_condition,
)
from .shape_func_helpers import(
    _function, _xs
)

def cylinderical_func_method(voltage, area, n0, V_s, m_i, KT_e, r_p=None, lambda_D=None, *args, correct_area=True, **kwargs):
    if correct_area is True:
        if r_p is None or lambda_D is None:
            raise ValueError("'r_p' and 'lambda_D' must be a float: " +
                             str(type(r_p))+" and "+str(type(lambda_D)))
        xs = _xs(voltage, V_s, KT_e, lambda_D)
        area = area*(1+xs/r_p)
    else:
        area = np.ones_like(voltage)*area

    # condition
    condition = cylinderical_domain_condition(voltage, V_s, KT_e)

    # I_i function
    func = _function

    # get I_i
    I_i = np.where(
        condition,
        func(area, n0, m_i, KT_e),
        0,
    )

    # make returns
    extras = {"method": "thin", "shape": "cylinderical"}
    return I_i, extras


def spherical_func_method(voltage, area, n0, V_s, m_i, KT_e, r_p=None, lambda_D=None, *args, correct_area=True, **kwargs):
    if correct_area is True:
        if r_p is None or lambda_D is None:
            raise ValueError("'r_p' and 'lambda_D' must be a float: " +
                             str(type(r_p))+" and "+str(type(lambda_D)))
        xs = _xs(voltage, V_s, KT_e, lambda_D)
        area = area*np.power(1+xs/r_p, 2)
    else:
        area = np.ones_like(voltage)*area

    # condition
    condition = spherical_domain_condition(voltage, V_s, KT_e)

    # I_i function
    func = _function

    # get I_i
    I_i = np.where(
        condition,
        func(area, n0, m_i, KT_e),
        0,
    )

    # make returns
    extras = {"method": "thin", "shape": "spherical"}
    return I_i, extras


def planar_func_method(voltage, area, n0, V_s, m_i, KT_e, r_p=None, lambda_D=None, *args, correct_area=True, **kwargs):
    if correct_area is True:
        pass  # no correction if oriented correctly
        if r_p is None or lambda_D is None:
            # not needed because no correction (filler for later if orientation bad)
            pass
        area = np.ones_like(voltage)*area
    else:
        area = np.ones_like(voltage)*area

    # condition
    condition = planar_domain_condition(voltage, V_s, KT_e)

    # I_i function
    func = _function

    # get I_i
    I_i = np.where(
        condition,
        func(area, n0, m_i, KT_e),
        0,
    )

    # make returns
    extras = {"method": "thin", "shape": "planar"}
    return I_i, extras