from pstl.utls.helpers import method_function_combiner
from pstl.utls.helpers import method_selector 

from .shape_methods import cylinderical_method, spherical_method, planar_method


def shape_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_methods, available_functions)
    return func

# Declare available methods
available_methods = {
    0: ['cylinderical', 'cylindrical'],
    1: ['spherical'],
    2: ['planar', 'planer'],
}
# Declare correspondin functions for available_methods
available_functions = {
    0: cylinderical_method,
    1: spherical_method,
    2: planar_method,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
options = method_function_combiner(available_methods, available_functions)