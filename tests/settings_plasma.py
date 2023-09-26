import pstl.utls.constants as c

from pstl.utls.plasmas import Plasma, NeonPlasma, ArgonPlasma, XenonPlasma

settings = {
    ""
    "m_i"   :           131.29*c.m_p,                   # amu -> kg
    "m_e"   :           c.m_e,                          # kg
    "netural_gas"   :   "Xenon",                        # Must be str
    "name"          :   "Rocket Chamber Background Gas",# Must be str
    "args"          :   (),                             # Tuple of position args
    "kwargs"        :   {}                              # Dict  of keyword args
}

setup = Plasma