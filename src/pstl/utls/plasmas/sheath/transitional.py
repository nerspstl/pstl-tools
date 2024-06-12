import numpy as np

from pstl.utls.helpers import method_function_combiner, method_selector


def shape_selector(shape):
    # select function based on integer_method
    func = method_selector(shape, available_shapes, available_shape_functions)
    return func


def cylinderical_ab(r_p, lambda_D, *args, **kwargs):
    ratio = r_p/lambda_D
    a = 1.18 - 0.00080*np.power(ratio, 1.35)
    b = 0.0684 + np.power(0.722+0.928*ratio, -0.729)
    return a, b


def spherical_ab(r_p, lambda_D, *args, **kwargs):
    ratio = r_p/lambda_D
    a = 1.58 + np.power(-0.056 + 0.816*ratio, -0.744)
    b = -0.933 + np.power(0.0148+0.119*ratio, -0.125)
    return a, b


def planar_ab(r_p, lambda_D, *args, **kwargs):
    ratio = r_p/lambda_D
    a = np.exp(-0.5)*np.sqrt(2*np.pi)*(2.28*np.power(ratio, -0.749))
    b = 0.806*np.power(ratio, -0.0692)
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
