from . import (
    thin,
    transitional,
    thick,
)
from .helpers import check_for_ion_current_fit
from .methods import (
    available_functions,
    available_methods,
    options,
)
from .methods import (
    get_ion_current,find_ion_current
)
from .methods import (
    thin_method, thin_func_method, transitional_method, thick_method,
)
from .methods_helpers import (default_fit_kwargs)

def info():
    msg = """
        rp: Radius of Probe
        LDe: Electron Debye Length

        Let rp/LDe = ratio

        Then
        If ratio <= 3       ->  Thick Sheath
        If 3 < ratio < 50   ->  Transitional Sheath
        If ratio >= 50      ->  Thin Sheath
        """
    print(msg)