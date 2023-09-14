"""

Testing get_plasma_potential func - funcs_plasma_potential.py


"""
from typing import Tuple, Dict, Any

import numpy as np
import numpy.typing as npt
from numpy.polynomial import Polynomial as P

from pstl.utls.verify import verify_type, verify_array_polarity
from pstl.utls.functionfit.helpers import _fit_exponential_func, find_fit, FunctionFit
from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import get_floating_potential
from pstl.diagnostics.probes.langmuir.single.analysis.electron_temperaure import get_electron_temperature
from pstl.diagnostics.probes.langmuir.single.analysis.electron_saturation_current import get_electron_saturation_current


def find_plasma_potential(*args, method: int | str | None = 0, **kwargs) -> float:
    value, _ = get_floating_potential(*args, method=method, **kwargs)
    return value


def get_plasma_potential(*args, method: int | str | None = 0, **kwargs) -> Tuple[float, Dict[str, Any]]:
    # Declare available method
    available_methods = {
        0: 'intersection',
    }

    # Converts method: str -> method: int if method is a str
    if isinstance(method, str):
        reversed_methods = {v: k for k, v in available_methods.items()}
        method = reversed_methods.get(method, None)

    # check for match and get which function to use
    # raises value error with options if failed to match
    if method == 0:  # default
        func = intersection_method
    else:  # makes a table of options if error occurs
        table = "\n".join([f"{k}\t{v}" for k, v in available_methods.items()])
        raise ValueError(
            f"Matching method not found: {method}\nChoose from one of the available options:\n{table}")

    # Call funtion and return result
    return func(*args, **kwargs)


def intersection_method(
        voltage, current, *args,
        V_f=None, elec_ret_poly=None, elec_sat_poly=None,
        **kwargs) -> Tuple[float, Dict[str, Any]]:

    # determine starting point (all positive after vf) if not given
    if V_f is None:
        # determine starting point (all positive after V_f)
        floating_kwargs = kwargs.pop('V_f_kwargs', {})
        floating_kwargs.setdefault('method', "consecutive")
        # get floating potential
        V_f, _ = get_floating_potential(
            voltage, current, **floating_kwargs)

    # make sure have Electron Retarding Region Polynomial of type ~np.polynomial.Polynomial
    if elec_ret_poly is None:
        KT_e_kwargs = kwargs.get("KT_e_kwargs", {})
        # set defaults for getting temperature
        KT_e_kwargs.setdefault('V_f', V_f)
        KT_e_kwargs.setdefault('V_s', None)
        KT_e_kwargs.setdefault('method', 'fit')
        # overide fit kwargs defaults for electron temperaure fit (exponential)
        KT_e_kwargs.setdefault('fit_kwargs',
                               {
                                   'full': False,
                               }
                               )
        _, KT_e_others = get_electron_temperature(
            voltage, current, **KT_e_kwargs)
        elec_ret_poly = KT_e_others["fit"].poly.convert()
    verify_type(elec_ret_poly, P)

    # make sure have Electron Saturation Region Polynomial of type ~np.polynomial.Polynomial
    if elec_sat_poly is None:
        I_es_kwargs = kwargs.get("I_es_kwargs", {})
        # set defaults for getting temperature
        I_es_kwargs.setdefault('V_f', V_f)
        I_es_kwargs.setdefault('V_s', None)
        I_es_kwargs.setdefault('method', 'fit')
        I_es_kwargs.setdefault('elec_ret_poly', elec_ret_poly)
        # overide fit kwargs defaults for electron temperaure fit (exponential)
        I_es_kwargs.setdefault('fit_kwargs',
                               {
                                   'full': False,
                               }
                               )
        _, I_es_others = get_electron_saturation_current(
            voltage, current, **I_es_kwargs)
        elec_sat_poly = I_es_others["fit"].poly.convert()
    verify_type(elec_sat_poly, P)

    # find intersection
    # intersection = find_intersection(elec_sat_fit, elec_sat_fit)
    p = elec_sat_poly-elec_ret_poly
    intersection = p.roots()

    # checks that instersection is made
    if intersection is None:
        raise ValueError("Intersection not found")

    # gets the plasma potential at intersection
    plasma_potential = intersection[0]

    # prepare returns
    others = {"method": "intersection"}
    # returns (value, other: Dict[str,Any])
    return plasma_potential, others
