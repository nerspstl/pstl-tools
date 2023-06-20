
from .ion_density import get_ion_density
from .electron_density import get_electron_density
from .plasma_potential import get_plasma_potential
from .electron_saturation_current import get_electron_saturation_current, get_electron_saturation_current_density
from .electron_temperaure import get_electron_temperature
from .ion_saturation_current import get_ion_saturation_current, get_ion_saturation_current_density
from .floating_potential import get_floating_potential
from .ion_current import get_ion_current
from pstl.utls.plasmas.sheath import get_probe_to_sheath_ratio
from typing import Dict, Any

import numpy as np
import pandas as pd

from pstl.utls import constants as c
from pstl.utls.constants import lambda_D as get_lambda_D
from pstl.utls.decorators import absorb_extra_args_kwargs, add_empty_dict
get_lambda_D = add_empty_dict(absorb_extra_args_kwargs(get_lambda_D))

default_plasma_properties_to_get = [
    "V_f",
    "V_s",
    "KT_e",
    "n_e",
    "I_es",
    "J_es",
    "n_i",
    "I_is",
    "J_is",
    "lambda_De",
    # "r_p/lambda_De",
    "sheath",
]
default_methods = {
    "V_f": "consecutive",
    "V_s": "intersection",
    "I_is": 0,
    "n_i": 0,
    "I_es": 0,
    "KT_e": 0,
    "n_e": 0,
    "J_es": 0,
    "J_is": 0,
    "lambda_De": 0,
    # "r_p/lambda_De": 0,
    "sheath": 0,
}


def print_results(results):
    for key, value in results.items():
        print(f"{key}:")
        for inner_key, inner_value in value.items():
            if key in ["n_i", "n_e", "I_is", "I_es", "J_es", "J_is", "lambda_De"] and inner_key == "value":
                if inner_value is not None:
                    print(f"\t{inner_key}: {inner_value:.2e}")
                else:
                    print(f"\t{inner_key}: {inner_value}")
            elif key in ["V_f", "V_s", "KT_e"] and inner_key == "value":
                if inner_value is not None:
                    print(f"\t{inner_key}: {inner_value:.2f}")
                else:
                    print(f"\t{inner_key}: {inner_value}")
            else:
                print(f"\t{inner_key}: {inner_value}")


def _return_orgainizer(returns):
    # check if tuple for indexing
    if isinstance(returns, tuple):
        value = returns[0]
        other = returns[1:]
    else:
        value = returns
        other = None
    return value, other


def get_plasma_property_sorter(key, method, *args, **kwargs):

    # choose which property
    if key == "V_f":
        func = get_floating_potential
    elif key == "V_s":
        func = get_plasma_potential
    elif key == "I_is":
        func = get_ion_saturation_current
    elif key == "n_i":
        func = get_ion_density
    elif key == "I_es":
        func = get_electron_saturation_current
    elif key == "KT_e":
        func = get_electron_temperature
    elif key == "n_e":
        func = get_electron_density
    elif key == "J_es":
        func = get_electron_saturation_current_density
    elif key == "J_is":
        func = get_ion_saturation_current_density
    elif key == "lambda_De":
        func = get_lambda_D
    elif key == "sheath":  # key == "r_p/lamda_De":
        func = get_probe_to_sheath_ratio
    else:
        table = "\n".join(
            [f"{k}\t{v}" for k, v in enumerate(default_methods)])
        raise ValueError(
            f"Matching key not found: {key}\nChoose from one of the available options:\n{table}")

    # solve and return a tuple
    return func(*args, method=method, **kwargs)


def lobbia():
    return


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
        shape,
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

######################################################################


def topham(voltage, current, shape, r_p, area, m_i, m_e=c.m_e,
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

    # inialize sheath method
    sheath_method = "thin"

    # Zero Step (optional):
    # smooth data for find better fit region

    # First Step:
    # Get Floating Potential
    # -> V_f
    key = "V_f"
    V_f, V_f_extras = get_floating_potential(
        voltage, current, method="consecutive", interpolate="linear",
    )

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
        shape,
        voltage, current,
        method=sheath_method, V_f=V_f,
    )
    I_i_fit = I_i_extras["fit"]

    I_e = np.subtract(current, I_i)

    convergence = False
    it = 0
    old = float("inf")
    while not convergence and it < itmax:
        # number of iterations
        it += 1

        # Second Step:
        # Find Rough Exponential Fit after Floating Potential in the Electron Retarding Region
        # Note: Ii is removed this should be only Ie
        # -> KT_e
        KT_e, KT_e_extras = get_electron_temperature(
            voltage, I_e, method="fit", V_f=V_f,
        )
        KT_e_poly = KT_e_extras["fit"].poly.convert()

        # Third Step:
        # Find Electron Saturation Exponential Fit
        # @ V_bias >> V_s (plasma or space potential) before probe breakdown (plasma created due to accelerated elcectrons),
        # There should be no ion current.
        # Note: Theory says I_es =
        # -> I_es = I_e(@V_s) = exp(m*V_s+b)
        I_es, I_es_extras = get_electron_saturation_current(
            voltage, I_e, method="fit", elec_ret_poly=KT_e_poly, V_f=V_f,
        )
        I_es_poly = I_es_extras["fit"].poly.convert()

        # Fourth Step:
        # Find Plasma Potential via intersection point of Electron Retarding and Saturation Regions
        # May also be done using first or second derivate to locate like in lobbia but requries smoothed data
        # and often inconclusive
        # -> V_s
        V_s, V_s_extras = get_plasma_potential(
            voltage, I_e, method="intersection", V_f=V_f, elec_ret_poly=KT_e_poly, elec_sat_poly=I_es_poly,
        )

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

        n_e, n_e_extras = get_electron_density(
            I_es, area, KT_e, m_e=c.m_e, method="I_es",
        )
        # get ionsaturation value at flaoting
        I_is, I_is_extras = get_ion_saturation_current(
            voltage, current, V_f=V_f, method="floating",
            I_i_fit=I_i_fit, I_i_method=sheath_method,
        )
        # temp ion density
        n_i, n_i_extras = get_ion_density(
            I_is, area, KT_e, m_i, method=sheath_method,
        )
        # lambda_D
        lambda_De, lambda_De_extras = get_lambda_D(n_e, KT_e)

        # ratio
        ratio, ratio_extras = get_probe_to_sheath_ratio(r_p, lambda_De)
        # sheath_method = ratio_extras["sheath"]

        # Repeat till Convergence on V_s from Intermediate Step to Last Step
        # using Ion Saturation Current fit to correct orginal probe current data to electron only current
        # i.e. I_probe,orginal - I_i,new = I_e,next_iteration_data
        if ratio <= 3:
            sheath_method = "thick"
        elif ratio > 3 and ratio < 50:
            sheath_method = "transitional"
            # get
        elif ratio >= 50 and it == 1:
            sheath_method = "thin"
            break
        elif ratio >= 50:
            errmsg = "Back to thin"
            raise ValueError(errmsg)
        else:
            errmsg = "WHa???!!!"
            raise ValueError(errmsg)

        if it == itmax:
            break

        # get updated n_i
        # <<enter here>>
        print(f"n_i before: {n_i:.2e}")
        n_i, n_i_extras = get_ion_density(
            voltage, current, area, m_i, KT_e, shape, r_p, lambda_De, shape, method=sheath_method)
        print(f"n_i after: {n_i:.2e}")

        # get new ion current with transitional or thick sheath
        print(I_i)
        print(I_i_extras)
        I_i, I_i_extras = get_ion_current(
            shape,
            voltage, current,
            method=sheath_method, V_f=V_f, n_i=n_i, n0=n_e, m_i=m_i, KT_e=KT_e, V_s=V_s,
        )
        # update I_is and I_is extras ## NEEEEEEEEDS ATTENETION
        I_is_extras['fit'] = I_i_extras["fit"]
        print(I_i)
        print(I_i_extras)

        new = lambda_De
        if it != 1:
            difference = old-new
            realtive_difference = difference/old
            RMSE = np.sqrt(np.sum(np.power(realtive_difference, 2)))
        else:
            RMSE = float("inf")
        old = new

        convergence = True if RMSE <= convergence_decimal else False

    results["V_f"]["value"] = V_f
    results["V_f"]["other"] = V_f_extras
    results["V_s"]["value"] = V_s
    results["V_s"]["other"] = V_s_extras
    results["I_is"]["value"] = I_is
    results["I_is"]["other"] = I_is_extras
    results["n_i"]["value"] = n_i
    results["n_i"]["other"] = n_i_extras
    results["I_es"]["value"] = I_es
    results["I_es"]["other"] = I_es_extras
    results["KT_e"]["value"] = KT_e
    results["KT_e"]["other"] = KT_e_extras
    results["n_e"]["value"] = n_e
    results["n_e"]["other"] = n_e_extras
    results["lambda_De"]["value"] = lambda_De
    results["lambda_De"]["other"] = lambda_De_extras
    # results["r_p/lambda_De"]["value"] = ratio
    # results["r_p/lambda_De"]["other"] = ratio_extras
    results["sheath"]["value"] = ratio
    results["sheath"]["other"] = ratio_extras
    data = {'voltage': voltage, 'current': current,
            'current_e': I_e, 'current_i': I_i}
    data = pd.DataFrame(data)
    return data, results
