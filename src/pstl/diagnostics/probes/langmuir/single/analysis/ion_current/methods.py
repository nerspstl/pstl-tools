from pstl.utls.helpers import method_selector
from pstl.utls.helpers import method_function_combiner

from . import thin, transitional, thick
#from .helpers import available_functions, available_methods

def find_ion_current(shape, *args, method=None, **kwargs):
    """
    Determines and returns only a 1D array of ion current contribution for each point of an IV trace. 
    Similar to get_ion_current, but no extras: dictionary is returned, just the 1D array of ion currents."""
    value, _ = get_ion_current(shape, method=method, *args, **kwargs)
    return value


def get_ion_current(shape, *args, method=None, ** kwargs):
    """
    Determines and returns a 1D array of ion current contribution for each point of an IV trace along with a dictionary with extras information.
    A default method is assumed unless specified via keyword argument 'method' to be 'thin_method'. The method's function is then called with
    argument 'shape', *args, **kwargs passed to the function. All called functions are templated to return ion_current: 1D array, extras: dictionary.
    """
    # set default -> (thin)
    method = 0 if method is None else method

    # select function based on integer_method
    func = method_selector(method, available_methods, available_functions)

    return func(shape, *args, **kwargs)

def thin_method(shape, *args, **kwargs):
    """
    Deterimes and then runs for the thin sheath ion current using a fitted experical function to the data.
    """
    func = thin.shape_fit_selector(shape)
    return func(*args, shape=shape,**kwargs)


def thin_func_method(shape, *args, **kwargs):
    """
    Determines and then runs for the thin sheath ion current using a theorical function to determine data.
    """
    func = thin.shape_func_selector(shape)
    return func(*args, shape=shape,**kwargs)


def transitional_method(shape, *args, **kwargs):
    func = transitional.shape_selector(shape)
    return func(*args, shape=shape,**kwargs)


def thick_method(shape, *args, **kwargs):
    func = thick.shape_selector(shape)
    return func(*args, shape=shape,**kwargs)

# Declare available methods
available_methods = {
    0: ['thin'],
    1: ['transitional'],
    2: ['thick', 'OML'],
    3: ['thin-func']
}
# Declare correspondin functions for available_methods
available_functions = {
    0: thin_method,
    1: transitional_method,
    2: thick_method,
    3: thin_func_method,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
options = method_function_combiner(available_methods, available_functions)