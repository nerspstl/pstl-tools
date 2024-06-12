import numpy as np

from pstl.utls import constants as c
#from pstl.utls.helpers import find_fit
from pstl.utls.functionfit import find_fit
from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import (
    check_for_floating_potential, get_below_floating_potential,
)

from .shape_fit_helpers import default_fit_linear_kwargs, default_fit_power_kwargs


def cylinderical_fit_method(voltage, current, *args, **kwargs):
    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.pop("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # I_i function
    fit_kwargs = dict(default_fit_power_kwargs)
    fit_kwargs["power"] = 0.75
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


def spherical_fit_method(voltage, current, *args, **kwargs):

    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.pop("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # I_i function
    fit_kwargs = dict(default_fit_power_kwargs)
    fit_kwargs["power"] = 1.5
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
    extras = {"fit": fit, "method": "thin", "shape": "spherical"}
    return I_i, extras


def planar_fit_method(voltage, current, *args, **kwargs):
    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.pop("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # I_i function
    fit_kwargs = dict(default_fit_linear_kwargs)
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
    extras = {"fit": fit, "method": "thin", "shape": "planar"}
    return I_i, extras


def linear_fit_method(voltage, current, *args, **kwargs):
    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.get("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # I_i function
    fit_kwargs = dict(default_fit_linear_kwargs)
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
    extras = {"fit": fit, "method": "thin-linear", "shape": "None"}
    return I_i, extras

