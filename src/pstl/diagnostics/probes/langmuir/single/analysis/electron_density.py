import numpy as np

import pstl.utls.constants as c


def get_electron_density(*args, method: int | str | None = 0, **kwargs):
    # Declare available methods
    available_methods = {
        0: 'I_es',
    }

    # Converts method: str -> method: int if method is a str
    if isinstance(method, str):
        reversed_methods = {v: k for k, v in available_methods.items()}
        method = reversed_methods.get(method, None)

    # check for match and get which function to use
    # raises value error with options if failed to match
    if method == 0:  # default
        func = thin_sheath_electron_saturation_current_method
    else:  # makes a table of options if error occurs
        table = "\n".join([f"{k}\t{v}" for k, v in available_methods.items()])
        raise ValueError(
            f"Matching method not found: {method}\nChoose from one of the available options:\n{table}")

    # Call funtion and return result
    return func(*args, **kwargs)


def thin_sheath_electron_saturation_current_method(I_es, area, KT_e, m_e=c.m_e, *args, **kwargs):
    # KT_e [eV]
    inv_root = np.sqrt(2*np.pi*m_e/(KT_e*c.K_B/c.K_B_eV))
    n_e = I_es*inv_root/(area*c.q_e)
    return n_e, {"method": "thin"}
