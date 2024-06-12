import numpy as np

# domain conditions ###########################################################
def cylinderical_domain_condition(voltage, V_s, KT_e):
    return _domain_condition(voltage, V_s, KT_e)


def spherical_domain_condition(voltage, V_s, KT_e):
    return _domain_condition(voltage, V_s, KT_e)


def planar_domain_condition(voltage, V_s, KT_e):
    return _domain_condition(voltage, V_s, KT_e)
###############################################################################

# generalized domain
def _domain_condition(voltage, V_s, KT_e):
    condition = np.divide(
        np.subtract(V_s, voltage),  # [V]
        KT_e                         # [eV]
    )
    return condition > 1  # >>1

