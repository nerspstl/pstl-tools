"""

Testing get_electron_temperature func - funcs_electon_temperature.py


"""

import numpy as np
import pprint

from pstl.utls.verify import verify_type
from pstl.utls.functionfit.helpers import find_fit
from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import get_floating_potential, check_for_floating_potential, get_above_floating_potential, get_positive_current

# defaults for 'find_fit' function
default_fit_kwargs = {
    'deg': 1, 'power': 1, 'polarity': 1,
    'reverse': False, 'return_best': True, 'fit_type': "exponential",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': None, 'fstep_type': None, 'fstep_adjust': True, 'fitmax': None,
    'bstep': None, 'bstep_type': None, 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.25,
    'threshold_rsq': 0.95, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 1.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}

# Declare available methods forthis module
available_methods = {
    0: 'fit',
}

def get_electron_temperature(*args, method: int | str | None = 0, **kwargs):

    # Converts method: str -> method: int if method is a str
    if isinstance(method, str):
        reversed_methods = {v: k for k, v in available_methods.items()}
        method = reversed_methods.get(method, None)

    # check for match and get which function to use
    # raises value error with options if failed to match
    if method == 0:  # default
        func = get_electron_temperature_fit
    else:  # makes a table of options if error occurs
        table = "\n".join([f"{k}\t{v}" for k, v in available_methods.items()])
        raise ValueError(
            f"Matching method not found: {method}\nChoose from one of the available options:\n{table}")

    # Call funtion and return result
    return func(*args, **kwargs)


def get_electron_temperature_fit(
        voltage, current, *args,
        V_f=None, V_s=None,
        **kwargs):

    # verify floating potential is a usable value if given else solve for floating potential
    #if V_f is not None:  # V_f is given and evaluated at this location
    #    verify_type(V_f, (int, float, np.int64, np.float64, np.ndarray), 'V_f')
    #else:
    #   # determine starting point (all positive after V_f)
    #    floating_kwargs = kwargs.pop('V_f_kwargs', {})
    #    floating_kwargs.setdefault('method', "consecutive")
    #    # get floating potential
    #    V_f, _ = get_floating_potential(
    #        voltage, current, **floating_kwargs)

    V_f = check_for_floating_potential(V_f,voltage,current,*args,**kwargs)

    # Once floating Potential is found, find its index w.r.t. data
    #istart = np.where(voltage < V_f)[0][-1]+1
    # Get data from positive current values (above floating)
    #xdata = voltage[istart:]
    #ydata = current[istart:]

    #istart, xdata, ydata = get_above_floating_potential(V_f,voltage, current,*args,**kwargs)
    n = 20
    istart, xdata, ydata = get_positive_current(n, voltage, current, *args, **kwargs)
    #pprint.pprint(np.where(ydata<0))

    # Set defaults for find fit search
    # sets default values for electron retarding fit, then updates with passed kwargs, then updates with fit_kwargs
    fit_kwargs = dict(default_fit_kwargs)
    fit_kwargs.update(kwargs.pop('fit_kwargs', {}))

    # solve for fit
    elec_ret_fit = find_fit(xdata, ydata, **fit_kwargs)

    # get electron temperature from fit polynomial conversion
    KTeV = 1/elec_ret_fit.poly.convert().coef[-1]

    # to return format (value, extras: Dict[str,Any])
    other = {"fit": elec_ret_fit}
    return KTeV, other
