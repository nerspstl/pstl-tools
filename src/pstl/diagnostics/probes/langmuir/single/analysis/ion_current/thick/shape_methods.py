import numpy as np

from pstl.utls.functionfit import make_CustomFit
from pstl.utls.decorators import where_function_else_zero
#from pstl.utls.helpers import find_fit
from pstl.utls.functionfit import find_fit
from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import (
    check_for_floating_potential, get_below_floating_potential,
)

from .shape_fit_helpers import default_fit_linear_kwargs, default_fit_power_kwargs

from .shape_domains import (
    cylinderical_domain_condition, 
    spherical_domain_condition, 
    planar_domain_condition,
    )
from .shape_helpers import (
    wrapper_cylinderical_function,
    wrapper_planar_function,
    wrapper_spherical_function,
)

def cylinderical_method(voltage, current, *args, **kwargs):
    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.pop("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # I_i function
    fit_kwargs = dict(default_fit_power_kwargs)
    fit_kwargs["power"] = 0.5
    fit_kwargs.update(kwargs.pop("fit_kwargs", {}))
    fit = find_fit(xdata, ydata, **fit_kwargs)
    # silence error when computing
    with np.errstate(invalid="ignore"):
        I_i = fit(voltage)

    # condition for I_i is negative
    condition = I_i <= 0

    # get I_i
    I_i = np.where(
        condition,
        I_i,
        0,
    )

    # make returns
    extras = {"fit": fit, "method": "thin", "shape": "cylinderical"}
    return I_i, extras

def cylinderical_func_method(voltage, area, n0, V_s, m_i, KT_e, *args, **kwargs):

    func = where_function_else_zero(
        wrapper_cylinderical_function, 
        cylinderical_domain_condition,
        )

    coefs = (V_s, KT_e, area, n0, m_i)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "thick", "shape": "cylinderical", "fit": fit}
    return I_i, extras

def spherical_method(voltage, current, *args, **kwargs):
    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.pop("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # I_i function
    fit_kwargs = dict(default_fit_linear_kwargs)
    fit_kwargs["power"] = 1
    fit_kwargs.update(kwargs.pop("fit_kwargs", {}))
    fit = find_fit(xdata, ydata, **fit_kwargs)
    # silence error when computing
    with np.errstate(invalid="ignore"):
        I_i = fit(voltage)

    # condition for I_i is negative
    condition = I_i <= 0

    # get I_i
    I_i = np.where(
        condition,
        I_i,
        0,
    )

    # make returns
    extras = {"fit": fit, "method": "thick", "shape": "spherical"}
    return I_i, extras


def spherical_func_method(voltage, area, n0, V_s, m_i, KT_e, *args, **kwargs):
    func = where_function_else_zero(
        wrapper_spherical_function, 
        spherical_domain_condition,
        )

    coefs = (V_s, KT_e, area, n0, m_i)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "thick", "shape": "spherical", "fit": fit}
    return I_i, extras

def planar_method(voltage, current, *args, **kwargs):

    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.pop("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # I_i function
    fit_kwargs = dict(default_fit_linear_kwargs)
    fit_kwargs["power"] = 1
    fit_kwargs.update(kwargs.pop("fit_kwargs", {}))
    fit = find_fit(xdata, ydata, **fit_kwargs)
    # silence error when computing
    with np.errstate(invalid="ignore"):
        I_i = fit(voltage)

    # condition for I_i is negative
    condition = I_i <= 0

    # get I_i
    I_i = np.where(
        condition,
        I_i,
        0,
    )

    # make returns
    extras = {"fit": fit, "method": "thick", "shape": "spherical"}
    return I_i, extras


def planar_func_method(voltage, area, n0, V_s, m_i, KT_e, *args, **kwargs):

    func = where_function_else_zero(
        wrapper_planar_function, 
        planar_domain_condition,
        )

    coefs = (V_s, KT_e, area, n0, m_i)
    I_i = func(voltage, *coefs)

    fit = make_CustomFit(func, voltage, I_i, coefs)

    # make returns
    extras = {"method": "thick", "shape": "planar", "fit": fit}
    return I_i, extras



