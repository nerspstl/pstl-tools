import numpy as np


m_p = 1.67262192369e-27  # kg
m_e = 9.1093837015e-31  # kg
q_e = 1.60217663e-19  # coulombs
e = 1.60217663e-19  # coulombs
q = 1.60217663e-19  # coulombs

# Boltzman Constant
K_B = 1.380649e-23  # J/K --or-- m2 kg s-2 K-1
K_B_eV = 8.617333262e-5  # eV/K

# Permitivity of free space
epsilon_0 = 8.85418782e-12  # m-3 kg-1 s4 A2

# Avogadro's Number
N_A = 6.02214076e23

# amu to kg
def amu_2_kg(amu):
    return np.divide(amu, N_A*1000)
def kg_2_amu(kg):
    return np.multiply(kg, N_A*1000)


# Debye length
def lambda_D(n, KT_e):
    # T_e : eV
    return np.sqrt(
        np.divide(
            np.multiply(KT_e*e, epsilon_0),
            np.multiply(n, np.multiply(q_e, q_e))
        )
    )
