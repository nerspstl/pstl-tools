

import numpy as np

from pstl.utls.helpers import method_function_combiner, method_selector


def shape_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_shapes, available_shape_functions)
    return func


def cylinderical_ab(*args, **kwargs):
    #a = 2*np.sqrt(np.pi) # In Lobbia paper it is defined as this one but I think it is wrong
    a = 2/np.sqrt(np.pi)
    b = 0.5
    return a, b


def spherical_ab(*args, **kwargs):
    return _thick_spherical_and_planar_ab()


def planar_ab(*args, **kwargs):
    return _thick_spherical_and_planar_ab()


def _thick_spherical_and_planar_ab(*args, **kwargs):
    a = 1
    b = 1
    return a, b


# Declare available methods
available_shapes = {
    0: ['cylinderical'],
    1: ['spherical'],
    2: ['planar','planer'],
}
# Declare correspondin functions for available_methods
available_shape_functions = {
    0: cylinderical_ab,
    1: spherical_ab,
    2: planar_ab,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
shape_options = method_function_combiner(
    available_shapes, available_shape_functions)
