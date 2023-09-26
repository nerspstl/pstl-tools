import numpy as np


from .methods import get_ion_current




def check_for_ion_current_fit(I_i_fit, voltage, current, shape=None, method=None, **kwargs):
    """
    Determines if there is function fit for ion current (I_i_fit). If it does not exist (i.e. I_i_fit is None),
    then a fit is made using suppied voltage, current, shape=None, method=None, kwargs['fit_kwargs'] to get_ion_current function.
    Returns a function fit class."""
    # determine starting point (all positive after vf) if not given
    if I_i_fit is None:
        # determine starting point (all positive after V_f)
        fit_kwargs = kwargs.pop('fit_kwargs', {})
        # get floating potential
        I_i, extras = get_ion_current(
            shape, voltage, current, method=method, fit_kwargs=fit_kwargs,
        )
        I_i_fit = extras["fit"]

    return I_i_fit



