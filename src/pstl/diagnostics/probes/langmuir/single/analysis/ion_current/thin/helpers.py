from pstl.utls.helpers import method_selector, method_function_combiner

from .shape_fit_methods import (
    cylinderical_fit_method,
    spherical_fit_method,
    planar_fit_method,
)
from .shape_func_methods import (
    cylinderical_func_method,
    spherical_func_method,
    planar_func_method,
)


def shape_fit_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_methods, available_fit_functions)
    return func


def shape_func_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_methods, available_func_functions)
    return func

# Declare available methods
available_methods = {
    0: ['cylinderical', 'cylindrical'],
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