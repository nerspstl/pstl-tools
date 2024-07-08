"""

Testing get_ion_saturation current func - funcs_ion_saturation_current.py


"""
from typing import Optional, Union, Tuple, Dict, Any

import numpy as np
import numpy.typing as npt

from pstl.utls import constants as c
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
        method: int | str | None = 0,
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
        3: 'combined',
        4: 'Ies',
        5: "minimum_fit",
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
    elif method == 3:
        func = combined_plasma_and_floating_method
    elif method == 4:
        func = calculate_ion_saturation_current_from_Ies
    elif method == 5:
        func = minimum_ion_current_fit_method
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

def _get_ion_current_fit(voltage, current, *args, I_i_fit=None,I_i_method=None,**kwargs):

    # check if fit needs to be found to evaluate at floating potential
    shape = kwargs.get("shape", None)
    fit_kwargs = kwargs.pop("fit_kwargs", {})
    I_i_fit = check_for_ion_current_fit(
        I_i_fit, voltage, current, shape, method=I_i_method, fit_kwargs=fit_kwargs)
    
    return I_i_fit


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

    I_i_fit= _get_ion_current_fit(voltage,current,*args,**kwargs)

    # Returns in formate (value, Dict[str,Any])
    other: dict[str, Any] = {"fit": I_i_fit}
    # Following set format of (value, Dict)
    return np.min(current), other


def minimum_ion_current_fit_method(
        voltage: npt.ArrayLike,
        current: npt.ArrayLike,
        *args, **kwargs) -> Tuple[float, Dict[str, Any]]:
    # maybe later add checks for:
    # 1) increasing current with increasing voltage (aka neg current to pos current)
    # 2) vectors same length
    # 3) no odd things in ion saturation region such as duplicates or spikes

    I_i_fit= _get_ion_current_fit(voltage,current,*args,**kwargs)
    Vmin = np.min(voltage)

    # Returns in formate (value, Dict[str,Any])
    other: dict[str, Any] = {"fit": I_i_fit}
    # Following set format of (value, Dict)
    return np.min(I_i_fit(Vmin)), other


def combined_plasma_and_floating_method(
        voltage, current, *args,
        V_s: float | None = None, return_V_s: bool = False, 
        V_f: float | None = None, return_V_f: bool = False, 
        T_e: float | None = None, return_T_e: bool = False, 
        n_e: float | None = None, return_n_e: bool = False, 
        area: float | None = None, return_area: bool = False, 
        **kwargs) -> Tuple[float, Dict[str, Any]]:
    # check if a plasma point is given, if non
    verify_pair_of_1D_arrays(voltage, current)
    if len(voltage) != len(current):
        raise ValueError(
            "Voltage and current arrays must have the same length.")

    # number of data points
    n = len(voltage)
    
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

    # solve for ion saturation current
    if V_s is not None:  # vs is given and evaluated at this location
        verify_type(V_s, (int, float, np.int64, np.float64, np.ndarray), 'V_s')
    else:
        # if vs is none get plasma potential via
        # get_plasma_potential_consecutive of funcs_plasma_potential
        plasma_kwargs = kwargs.get('plasma_kwargs', {})
        V_s, _ = get_plasma_potential(
            voltage, current, **plasma_kwargs)

    # calculate ion_saturation_current
    ion_saturation_current = _combined_get_ion_saturation_current(n_e,area,T_e,V_f,V_s)

    I_i_fit= _get_ion_current_fit(voltage,current,*args,**kwargs)

    # Returns in formate (value, Dict[str,Any])
    other: dict[str, Any] = {"fit": I_i_fit}
    if return_V_s is True:
        other['V_s'] = V_s
    if return_V_f is True:
        other['V_f'] = V_f
    if return_T_e is True:
        other['T_e'] = T_e
    if return_n_e is True:
        other['n_e'] = n_e
    if return_area is True:
        other['area'] = area
    return ion_saturation_current, other

def calculate_ion_saturation_current_from_Ies(voltage, current,*args, **kwargs) -> tuple[float, dict[str, Any]]:
    electron_sat = kwargs.pop("electron_sat", None)
    amu = kwargs.pop("amu", None)
    ion_sat: float = -np.divide(electron_sat, amu)
    if ion_sat is np.nan:
        raise ValueError
    I_i_fit= _get_ion_current_fit(voltage,current,*args,**kwargs)

    # Returns in formate (value, Dict[str,Any])
    other: dict[str, Any] = {"fit": I_i_fit}
    return ion_sat, other

def calculate_ion_saturation_current_xenon(electron_sat) -> float:
    ion_sat = -np.divide(electron_sat, 131.29)
    if ion_sat is np.nan:
        raise ValueError
    return ion_sat

def _combined_get_ion_saturation_current(n,area,T_e,V_f,V_s):
    # T_e is eV
    I_es = c.e*n*area*np.sqrt((c.e*T_e)/(2*np.pi*c.m_e))
    I_e = I_es*np.exp(c.e*(V_f-V_s)/(T_e*c.e))
    I_isat = -I_e # @ floating potential
    return I_isat