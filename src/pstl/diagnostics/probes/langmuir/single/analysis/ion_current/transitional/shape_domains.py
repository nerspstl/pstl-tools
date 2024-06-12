import numpy as np

# domain conditions
def cylinderical_domain_condition(voltage, V_s, KT_e):
    return _cylinderical_spherical_domain_condition(voltage, V_s, KT_e)


def spherical_domain_condition(voltage, V_s, KT_e):
    return _cylinderical_spherical_domain_condition(voltage, V_s, KT_e)

def planar_domain_condition(voltage, V_s, KT_e):
    condition = np.divide(
        np.subtract(V_s, voltage),  # [V]
        KT_e                         # [eV]
    )

    cond1 = 3 < condition
    cond2 = condition < 30
    return np.logical_and(cond1, cond2)  # 10 < rp/l < 45

# generalized domain
def _cylinderical_spherical_domain_condition(voltage, V_s, KT_e):
    condition = np.divide(
        np.subtract(V_s, voltage),  # [V]
        KT_e                         # [eV]
    )
    return condition > 1
