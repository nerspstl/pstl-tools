import numpy as np

# domain conditions
def cylinderical_domain_condition(voltage, V_s, KT_e, *args, **kwargs):
    return _domain_condition(voltage, V_s, KT_e, *args, **kwargs)


def spherical_domain_condition(voltage, V_s, KT_e, *args, **kwargs):
    return _domain_condition(voltage, V_s, KT_e, *args, **kwargs)


def planar_domain_condition(voltage, V_s, KT_e, *args, **kwargs):
    return _domain_condition(voltage, V_s, KT_e, *args, **kwargs)

# generalized domain


def _domain_condition(voltage, V_s, KT_e, *args, **kwargs):
    condition = np.divide(
        np.subtract(V_s, voltage),  # [V]
        KT_e                         # [eV]
    )
    return condition > 1  # >>1