from typing import Dict, Any

import numpy as np

from pstl.utls import constants as c

from .algorithm_helpers import(
    get_plasma_property_sorter,
)
from .algorithm_helpers import(
    default_methods,
    default_plasma_properties_to_get,
)

from ..ion_current import get_ion_current

def _topham(voltage, current, area, m_i, m_e=c.m_e,
            methods={},
            smooth=False, itmax=1, convergence_percent=1,
            *args, **kwargs) -> Dict:
    properties = None
    if not isinstance(methods, dict):
        raise ValueError(
            "'methods' must be a dictionary not: ", type(methods))
    # convert convergence percent to a decimal
    convergence_decimal = convergence_percent/100

    # overwrite methods if passed in
    methods_to_use = dict(default_methods)
    methods_to_use.update(methods)

    # overwrite properties if passed in (not implemented yet)
    if properties is None:
        properties_to_get = list(default_plasma_properties_to_get)
    elif isinstance(properties, list):
        properties_to_get = list(properties)
    else:
        raise ValueError(
            "'properteies' must be a list or None not: ", type(methods))

    # set up results dictionary for returns
    results = {}
    for plasma_property in properties_to_get:
        results[plasma_property] = {'value': None, 'other': None}

    # see what kwargs are given and creat a new dictionary
    func_kwargs = {}
    for key in methods_to_use.keys():
        func_kwargs[key] = kwargs.get(key+"_kwargs", {})

    # Zero Step (optional):
    # smooth data for find better fit region

    # First Step:
    # Get Floating Potential
    # -> V_f
    key = "V_f"
    results[key]["value"], results[key]["other"] = get_plasma_property_sorter(
        key, methods_to_use[key], *args, **func_kwargs[key])

    # Intermediate Step (optional for convergence speedup):
    # Do Either @ V_bias << V_f:
    # 1) Fit a linear line in Ion Saturation Region
    # 2) Take the resonable minimum value of the Ion Saturation Region
    # 3) Fit a power term (i.e. 1/2) to the Ion Saturation Region
    # Then either use the fits to subtract out ion current from the total probe current
    # to get a approximate electron only current, or a flat value across the board of the
    # minimum ion current (may lead to artifcial bi-Maxwellian)
    # Ie = Iprobe - Ii  --or-- Iprobe = Ie+Ii (note: Ii convention is negative)
    # -> temp I_i
    I_i, I_i_extras = get_ion_current(
        "spherical",
    )

    convergence = False
    it = 0
    vs_old = float("inf")
    key_convergence = "V_s"
    while not convergence and it < itmax:
        # number of iterations
        it += 1

        # Second Step:
        # Find Rough Exponential Fit after Floating Potential in the Electron Retarding Region
        # Note: Ii is removed this should be only Ie
        # -> KT_e

        # Third Step:
        # Find Electron Saturation Exponential Fit
        # @ V_bias >> V_s (plasma or space potential) before probe breakdown (plasma created due to accelerated elcectrons),
        # There should be no ion current.
        # Note: Theory says I_es =
        # -> I_es = I_e(@V_s) = exp(m*V_s+b)

        # Fourth Step:
        # Find Plasma Potential via intersection point of Electron Retarding and Saturation Regions
        # May also be done using first or second derivate to locate like in lobbia but requries smoothed data
        # and often inconclusive
        # -> V_s

        # Fifth Step:
        # Find Ion Saturation Current
        # Either:
        # 1) Thin Sheath:
        #   Linear Ion Saturation Fit @ V_bias << V_f that intersects the x-axis at a V_bias > V_s
        #   -> I_is = I_i(@V_s) = m*V_s + b
        # 2) Thick Sheath/Orbital Motion Limited (OML):
        #   Power 1/2 Fit in the Ion Saturation Region @ V_bias << V_f
        #   I_i^2 = alpha*V_bias + beta
        #       Where: alpha = -(q_e*area*ni)^2*(2.1*q_e/(pi^2*m_i))
        #               beta = (q_e*area*ni)^2*(2.1*q_e/(pi^2*m_i))*V_s
        #   Note: in theory I_es = -I_is*exp(0.5)*sqrt(m_i/(2*pi*m_e))
        # questionable below:
        #   -> I_is = -I_es*exp(-0.5)*sqrt(2*pi*m_e/m_i) --or-- I_is = -exp(-0.5)*area*q_e*n_i*sqrt(KT_e/m_i)

        # combines while loop steps into a few lines
        for key in ["KT_e", "I_es", "V_s", "I_is"]:
            results[key]["value"], results[key]["other"] = get_plasma_property_sorter(
                key, methods_to_use[key], *args, **func_kwargs[key])

        # Repeat till Convergence on V_s from Intermediate Step to Last Step
        # using Ion Saturation Current fit to correct orginal probe current data to electron only current
        # i.e. I_probe,orginal - I_i,new = I_e,next_iteration_data

        vs_new = results[key_convergence]['value']
        difference = vs_old-vs_new
        realtive_difference = difference/vs_old
        abs_rel_diff = np.abs(realtive_difference)

        convergence = True if abs_rel_diff <= convergence_decimal else False

    # Last Step:
    # Once convergence is made, get n_i and n_e (ion and electron densities) and J_es and J_is (electorn and ion saturation current densities)
    # Electrons:
    # -> n_e = I_es/(area*q_e)*sqrt(2*pi*m_e/KT_e)
    # -> J_es = I_es/area
    # Ions:
    # if thin sheath:
    # n_i = I_is/(area*q_e)*sqrt(m_i/KT_e)
    # if thick sheath:
    # n_i = ((alpha*pi^2*m_i)/(2*q_e^3*area^2))^(0.5)

    # Debye Length
    # -> lambda_De = sqrt(KT_e*epsilon_0/(n_e*q_e^2))

    # combines while loop steps into a few lines
    for key in ["n_e", "n_i", "J_es", "J_is", "lambda_De"]:
        results[key]["value"], results[key]["other"] = get_plasma_property_sorter(
            key, methods_to_use[key], *args, **func_kwargs[key])

    return results