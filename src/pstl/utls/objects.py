from typing import Any, Callable, Iterable
import pprint

from pstl.utls.json import load_build_and_get_parameters

def loop_key(settings, keys):
    if len(keys) != 0:
        output = loop_key(settings[keys[0]], keys.remove(keys[0]))
    else:
        output = settings
    return output

    
        


def extract_to_args(definer, settings):
    export = dict(definer)
    for key in definer:
        export[key] = loop_key(settings,definer[key])

    return export

def setup(
        settings:   dict, 
        builders:   dict[str, Any],
        Builder:    Any,
        *args, 
        to_args:    dict[str, list[str]] = {},
        **kwargs) -> Any:
    
    # get parameters by loading and/or building from file
    parameters = load_build_and_get_parameters(
        *args,
        settings=settings,
        builders=builders,
        **kwargs,
    )

    # using the to_args dictionary after everything is built
    extracted_to_args = extract_to_args(to_args, settings) if len(to_args) != 0 else {} 
    
    # creates object from parameters (sourced from settings)
    output: Any = Builder(
        *args, 
        **extracted_to_args,
        **parameters, 
        **kwargs,
    )

    return output

