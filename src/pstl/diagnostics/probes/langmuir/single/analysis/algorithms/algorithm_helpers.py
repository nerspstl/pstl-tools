from pstl.utls.constants import lambda_D as get_lambda_D
from pstl.utls.decorators import absorb_extra_args_kwargs, add_empty_dict
get_lambda_D = add_empty_dict(absorb_extra_args_kwargs(get_lambda_D))
from pstl.utls.plasmas.sheath import get_probe_to_sheath_ratio
from ..ion_density import get_ion_density
from ..electron_density import get_electron_density
from ..plasma_potential import get_plasma_potential
from ..electron_saturation_current import get_electron_saturation_current, get_electron_saturation_current_density
from ..electron_temperaure import get_electron_temperature
from ..ion_saturation_current import get_ion_saturation_current, get_ion_saturation_current_density
from ..floating_potential import get_floating_potential
from ..ion_current import get_ion_current

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
    "r_p/lambda_De",
    "sheath",
]
default_methods = {
    "V_f": "consecutive",
    "V_s": "intersection",
    "I_is": 3,
    "n_i": 0,
    "I_es": 0,
    "KT_e": 0,
    "n_e": 0,
    "J_es": 0,
    "J_is": 0,
    "lambda_De": 0,
    "r_p/lambda_De": 0,
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

def topham_configure(convergence_percent, methods,*args, **kwargs):
    """
    This function calls other functions and then returns all of the 
    the initial configurations for the topham algorithm for solving a
    Langmuir probe.

    Parameters:
    convergence_percent     "The convergence criteria in percent of the
                            Langmuir algorithm for changes in sheath"
    methods                 "Dictionary of methods for solving for 
                            plasma properties"
    *args
    **kwargs                "Function args/kwargs for methods"

    Returns:
    convergence_decimal
    methods_to_use
    properties_to_get
    results
    func_kwargs
    """
    # Initialized plasma properties to return (not yet implemented)
    properties = None

    # Checks defined methods are in a dictionary
    if not isinstance(methods, dict):
        raise ValueError(
            "'methods' must be a dictionary not: ", type(methods))
    
    # convert convergence percent to a decimal
    convergence_decimal = convergence_percent/100

    # overwrite default methods to be used if methods is partially/fully defined
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

    # tuple of returns
    returns = (
        convergence_decimal,
        methods_to_use,
        properties_to_get,
        results,
        func_kwargs,
    )

    return returns


def topham_get_ion_current_and_density(
        voltage, current, shape, sheath_method, area, m_i,KT_e, 
        r_p, lambda_De, V_f, V_s, n_e, n_i):
    """
    NEEDS WORK, but it works
    Only for transitional and thick sheaths
    """
    print(f"n_i before: {n_i:.2e}")
    n_i, n_i_extras = get_ion_density(
        voltage, current, area=area, m_i=m_i, KT_e=KT_e, shape=shape, r_p=r_p, lambda_De=lambda_De, method=sheath_method)
    print(f"n_i after: {n_i:.2e}")

    # get new ion current with transitional or thick sheath
    I_i, I_i_extras = get_ion_current(
        shape,
        voltage,current=current,
        method=sheath_method, V_f=V_f, n_i=n_i, n0=n_e, m_i=m_i, KT_e=KT_e, V_s=V_s, area=area,
    )
    return I_i, I_i_extras, n_i, n_i_extras
