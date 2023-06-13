"""

Testing get_ion_saturation current func - funcs_ion_saturation_current.py


"""
from typing import Optional, Union, Tuple, Dict, Any

import numpy as np
import numpy.typing as npt

from pstl.utls.verify import verify_type, verify_pair_of_1D_arrays
from pstl.utls.functionfit.helpers import find_fit, FunctionFit

from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import get_floating_potential, check_for_floating_potential, get_below_floating_potential
from pstl.diagnostics.probes.langmuir.single.analysis.plasma_potential import get_plasma_potential
from pstl.diagnostics.probes.langmuir.single.analysis.ion_current import check_for_ion_current_fit


default_fit_thin_kwargs = {
    'deg': 1, 'power': 1, 'polarity': 1,
    'reverse': False, 'return_best': True, 'fit_type': "linear",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': None, 'fstep_type': None, 'fstep_adjust': True, 'fitmax': None,
    'bstep': None, 'bstep_type': None, 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.30,
    'threshold_rsq': 0.95, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 1.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}

default_fit_thick_kwargs = {
    'deg': 1, 'power': 0.5, 'polarity': -1,
    'reverse': False, 'return_best': True, 'fit_type': "linear",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': None, 'fstep_type': None, 'fstep_adjust': True, 'fitmax': None,
    'bstep': None, 'bstep_type': None, 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.30,
    'threshold_rsq': 0.95, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 1.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}


def get_ion_saturation_current(
        *args,
        method: int | str = 0,
        **kwargs) -> Tuple[float, Dict[str, Any]]:
    """
    Parameters
    ----------
    method: str, optional
        if 'min' or 'minimum', then returns the the lowest current
        if 'vf' or 'floating', then returns the value at floating 
        potential voltage from a linear fit line that matches the 
        specified r^2, default r^2=0.95
    """
    # Declare available methods
    available_methods = {
        0: 'plasma',
        1: 'floating',
        2: 'minimum',
    }

    # Converts method: str -> method: int if method is a str
    if isinstance(method, str):
        reversed_methods = {v: k for k, v in available_methods.items()}
        # if method:str is not in avialiable_methods,
        # it will error out in check as it is set to the default and will not match
        method = reversed_methods.get(method, method)

    # check for match and get which function to use
    # raises value error with options if failed to match
    if method == 0:  # default
        func = plasma_potential_method
    elif method == 1:
        func = floating_potential_method
    elif method == 2:
        func = minimum_ion_current_method
    else:  # makes a table of options if error occurs
        table = "\n".join([f"{k}\t{v}" for k, v in available_methods.items()])
        raise ValueError(
            f"Matching method not found: {method}\nChoose from one of the available options:\n{table}")

    # Call funtion and return result
    return func(*args, **kwargs)


def get_ion_saturation_current_density(area, *args, method=0, I_is=None, **kwargs):
    if I_is is None:
        value, other = get_ion_saturation_current(
            *args, method=method, **kwargs)
        I_is = value
    else:
        other = {}
    J_is = np.divide(I_is, area)
    return J_is, other


def plasma_potential_method(
        voltage, current, *args,
        V_s: float | None = None, return_V_s: bool = False, I_es: float | None = None,
        **kwargs) -> Tuple[float, Dict[str, Any]]:
    # check if a plasma point is given, if non
    verify_pair_of_1D_arrays(voltage, current)
    if len(voltage) != len(current):
        raise ValueError(
            "Voltage and current arrays must have the same length.")

    # number of data points
    n = len(voltage)

    j = 0
    # Find the first transition point from negative to positive or zero current
    while j < n and current[j] < 0:
        j += 1

    # set some defaults for routine
    fit_kwargs = dict(default_fit_thin_kwargs)
    fit_kwargs.update(kwargs.pop('fit_kwargs', {}))
    # thus j now is where current transitions from negative to postive
    # loop through the points fitting a line
    # fit = routine_linear_fit(voltage[0:j], current[0:j], **kwargs)
    fit = find_fit(voltage[0:j], current[0:j], **fit_kwargs)

    # solve for ion saturation current
    if V_s is not None:  # vs is given and evaluated at this location
        verify_type(V_s, (int, float, np.int64, np.float64, np.ndarray), 'V_s')
    else:
        # if vs is none get plasma potential via
        # get_plasma_potential_consecutive of funcs_plasma_potential
        plasma_kwargs = kwargs.get('plasma_kwargs', {})
        V_s, _ = get_plasma_potential(
            voltage, current, **plasma_kwargs)

    # use plasma potential to find saturation current
    ion_saturation_current = fit(V_s)

    # if nan or positive
    if ion_saturation_current > 0 or np.isnan(ion_saturation_current):
        if I_es is None:
            raise NotImplementedError
        ion_saturation_current = calculate_ion_saturation_current_xenon(I_es)

    # Returns in formate (value, Dict[str,Any])
    other: dict[str, Any] = {"fit": fit}
    if return_V_s is True:
        other['V_s'] = V_s
    return ion_saturation_current, other


def floating_potential_method(
        voltage, current, *args,
        I_i_fit=None, I_i_method=None,
        V_f: float | None = None, return_V_f: bool = False,
        **kwargs) -> Tuple[float, Dict[str, Any]]:
    # check if a floating point is given, if non
    # verify arrays length and shape
    verify_pair_of_1D_arrays(voltage, current)
    if len(voltage) != len(current):
        raise ValueError(
            "Voltage and current arrays must have the same length.")

    # check  and setup xdata,ydata based on floaing potential
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    # check if fit needs to be found to evaluate at floating potential
    shape = kwargs.get("shape", None)
    fit_kwargs = kwargs.pop("fit_kwargs", {})
    I_i_fit = check_for_ion_current_fit(
        I_i_fit, voltage, current, shape, method=I_i_method, fit_kwargs=fit_kwargs)

    # use V_f to find saturation current
    ion_saturation_current = I_i_fit(V_f)

    # Returns in formate (value, Dict[str,Any])
    other: dict[str, Any] = {"fit": I_i_fit}
    if return_V_f is True:
        other['V_f'] = V_f
    return ion_saturation_current, other


def _floating_potential_method(
        voltage, current, *args,
        V_f: float | None = None, return_V_f: bool = False,
        **kwargs) -> Tuple[float, Dict[str, Any]]:
    # check if a floating point is given, if non
    # verify arrays length and shape
    verify_pair_of_1D_arrays(voltage, current)
    if len(voltage) != len(current):
        raise ValueError(
            "Voltage and current arrays must have the same length.")

    # number of data points
    n = len(voltage)

    j = 0
    # Find the first transition point from negative to positive or zero current
    while j < n and current[j] < 0:
        j += 1

    # thus j now is where current transitions from negative to postive
    # loop through the points fitting a line
    # fit = routine_linear_fit(voltage[0:j], current[0:j], **kwargs)
    fit = find_fit(voltage[0:j], current[0:j], **kwargs)

    # determine starting point (all positive after vf) if not given
    if V_f is None:
        # determine starting point (all positive after V_f)
        floating_kwargs = kwargs.pop('V_f_kwargs', {})
        floating_kwargs.setdefault('method', "consecutive")
        # get floating potential
        V_f, _ = get_floating_potential(
            voltage, current, **floating_kwargs)
    # verify V_f
    verify_type(V_f, (int, float, np.int64, np.float64, np.ndarray), 'V_f')

    # use V_f to find saturation current
    ion_saturation_current = fit(V_f)

    # Returns in formate (value, Dict[str,Any])
    other: dict[str, Any] = {"fit": fit}
    if return_V_f is True:
        other['V_f'] = V_f
    return ion_saturation_current, other


def minimum_ion_current_method(
        voltage: npt.ArrayLike,
        current: npt.ArrayLike,
        *args, **kwargs) -> Tuple[float, Dict[str, Any]]:
    # maybe later add checks for:
    # 1) increasing current with increasing voltage (aka neg current to pos current)
    # 2) vectors same length
    # 3) no odd things in ion saturation region such as duplicates or spikes

    # Following set format of (value, Dict)
    return np.min(current), {}


def calculate_ion_saturation_current_xenon(electron_sat) -> float:
    ion_sat = -np.divide(electron_sat, 323)
    if ion_sat is np.nan:
        raise ValueError
    return ion_sat
