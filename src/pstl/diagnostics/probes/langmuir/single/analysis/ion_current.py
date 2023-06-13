import numpy as np

from pstl.utls import constants as c
from .utls.ion_current import thin, thick, transitional
from pstl.utls.helpers import method_selector
from pstl.utls.helpers import method_function_combiner
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


def find_ion_current(shape, *args, method=None, **kwargs):
    value, _ = get_ion_current(shape, method=method, *args, **kwargs)
    return value


def get_ion_current(shape, *args, method=None, ** kwargs):

    # set default -> (thin)
    method = 0 if method is None else method

    # select function based on integer_method
    func = method_selector(method, available_methods, available_functions)

    return func(shape, *args, **kwargs)


def check_for_ion_current_fit(I_i_fit, voltage, current, shape=None, method=None, **kwargs):
    # determine starting point (all positive after vf) if not given
    if I_i_fit is None:
        # determine starting point (all positive after V_f)
        fit_kwargs = kwargs.pop('fit_kwargs', {})
        # get floating potential
        I_i, extras = get_ion_current(
            shape, voltage, current, method=method, fit_kwargs=fit_kwargs,
        )
        I_i_fit = extras["fit"]

    return I_i_fit


def thin_method(shape, *args, **kwargs):
    func = thin.shape_fit_selector(shape)
    return func(*args, **kwargs)


def thin_func_method(shape, *args, **kwargs):
    func = thin.shape_func_selector(shape)
    return func(*args, **kwargs)


def transitional_method(shape, *args, **kwargs):
    func = transitional.shape_selector(shape)
    return func(*args, **kwargs)


def thick_method(shape, *args, **kwargs):
    func = thick.shape_selector(shape)
    return func(*args, **kwargs)


# Declare available methods
available_methods = {
    0: ['thin'],
    1: ['transitional'],
    2: ['thick', 'OML'],
    3: ['thin-func']
}
# Declare correspondin functions for available_methods
available_functions = {
    0: thin_method,
    1: transitional_method,
    2: thick_method,
    3: thin_func_method,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
options = method_function_combiner(available_methods, available_functions)
