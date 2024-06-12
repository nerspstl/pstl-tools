
import numpy as np
from numpy.polynomial import Polynomial as P

from pstl.utls import constants as c
from pstl.utls.functionfit.helpers import find_fit
from pstl.utls.plasmas.sheath import thick, transitional
from pstl.utls.helpers import method_selector, method_function_combiner

from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import check_for_floating_potential, get_below_floating_potential
from pstl.diagnostics.probes.langmuir.single.analysis.ion_current import default_fit_kwargs


def get_ion_density(*args, method: int | str | None = 0, **kwargs):
    # set default -> (thin)
    method = 0 if method is None else method

    # select function based on integer_method
    func = method_selector(method, available_methods, available_functions)

    # Call funtion and return result
    return func(*args, **kwargs)


def thin_sheath_method(I_is, area, KT_e, m_i, shape="Unknown", *args, **kwargs):
    # KT_e [eV]
    inv_root = np.sqrt(m_i/(KT_e*c.e))
    # np.exp(-0.5) = 1/np.exp(0.5) = 0.61
    n_i = np.abs(I_is)*inv_root/(area*c.q_e)*np.exp(0.5)
    return n_i, {"method": "thin", "shape": shape}


def transitional_sheath_method(voltage, current, area, m_i, KT_e, shape, r_p, lambda_De, *args, **kwargs):
    func = transitional.shape_selector(shape)
    a, b = func(r_p, lambda_De)
    n_i = _transitional_and_thick_method(
        voltage, current, area, m_i, KT_e, a, b)
    return n_i, {"method": "transitional", "shape": shape}


def thick_sheath_method(voltage, current, area, m_i, KT_e, shape, *args, **kwargs):
    func = thick.shape_selector(shape)
    a, b = func()
    n_i = _transitional_and_thick_method(
        voltage, current, area, m_i, KT_e, a, b)
    return n_i, {"method": "thick", "shape": shape}

def _transitional_and_thick_method(voltage, current, area, m_i, KT_e, a, b, **kwargs):
    # check  and setup xdata,ydata based on floaing potential
    V_f = kwargs.pop("V_f", None)
    V_f = check_for_floating_potential(V_f, voltage, current, **kwargs)
    iend, xdata, ydata = get_below_floating_potential(V_f, voltage, current)

    ydata_mod = np.power(ydata*-1, 1/b)

    # I_i function
    fit_kwargs = dict(default_fit_kwargs["thick"])
    fit_kwargs["power"] = 1
    fit_kwargs["polarity"] = 1
    fit_kwargs.update(kwargs.pop("fit_kwargs", {}))
    fit = find_fit(xdata, ydata_mod, **fit_kwargs)
    A = 1/(a*area)*np.sqrt(2*np.pi*m_i) * \
        np.power(c.e, -1.5)*np.power(KT_e, b-0.5)
    slope = fit.coef[-1]
    n_i = np.multiply(A, np.power(-slope, b))
    return n_i

def _transitional_and_thick_method_upto_floating(voltage, current, area, m_i, KT_e, a, b):
    I = current[current<0]*-1
    V = voltage[current<0]
    A = 1/(a*area)*np.sqrt(2*np.pi*m_i) * \
        np.power(c.e, -1.5)*np.power(KT_e, b-0.5)
    mod_I_probe = np.power(I, 1/b)
    polyfit = P.fit(V, mod_I_probe, deg=1)
    slope = polyfit.convert().coef[-1]
    n_i = np.multiply(A, np.power(-slope, b))
    return n_i


# Declare available methods
available_methods = {
    0: ['thin'],
    1: ['transitional'],
    2: ['thick', 'OML'],
}
# Declare correspondin functions for available_methods
available_functions = {
    0: thin_sheath_method,
    1: transitional_sheath_method,
    2: thick_sheath_method,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
options = method_function_combiner(available_methods, available_functions)
