import numpy as np

from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import check_for_floating_potential, get_below_floating_potential
from pstl.utls import constants as c
from pstl.utls.helpers import method_function_combiner
from pstl.utls.helpers import method_selector as method_selector
from pstl.utls.helpers import find_fit
from pstl.utls.helpers import FunctionFit


default_fit_linear_kwargs = {
    'deg': 1, 'power': 1, 'polarity': 1,
    'reverse': False, 'return_best': True, 'fit_type': "linear",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': None, 'fstep_type': None, 'fstep_adjust': True, 'fitmax': None,
    'bstep': None, 'bstep_type': None, 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.30,
    'threshold_rsq': 0.85, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 10.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}

default_fit_power_kwargs = {
    'deg': 1, 'power': None, 'polarity': -1,  # power needs to be defined
    'reverse': False, 'return_best': True, 'fit_type': "power",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': None, 'fstep_type': None, 'fstep_adjust': True, 'fitmax': None,
    'bstep': None, 'bstep_type': None, 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.50,
    'threshold_rsq': 0.95, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 10.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}


def shape_fit_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_methods, available_fit_functions)
    return func


def shape_func_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_methods, available_func_functions)
    return func


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


def _xs(voltage, V_s, KT_e, lambda_D):
    A = lambda_D*np.sqrt(2)/3
    x = 2*(V_s-voltage)/KT_e
    with np.errstate(invalid="ignore"):
        power_x = np.power(x, 0.75)
    return np.multiply(A, power_x)


def _function(area, n0, m_i, KT_e):
    return np.exp(-0.5)*c.e*n0*area*np.sqrt(c.e*KT_e/m_i)


def _constant_function(voltage, current, *args, **kwargs):
    return np.ones_like(voltage)*_function(*args)


# Declare available methods
available_methods = {
    0: ['cylinderical'],
    1: ['spherical'],
    2: ['planar', 'planer'],
}
# declare correspondin functions for available_methods
available_fit_functions = {
    0: cylinderical_fit_method,
    1: spherical_fit_method,
    2: planar_fit_method,
}
# declare correspondin functions for available_methods
available_func_functions = {
    0: cylinderical_func_method,
    1: spherical_func_method,
    2: planar_func_method,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
fit_options = method_function_combiner(
    available_methods, available_fit_functions)

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
func_options = method_function_combiner(
    available_methods, available_func_functions)
