from pstl.utls import constants as c
from pstl.utls.objects import setup as object_setup

available_plasma_classes = {
    0   :   ["custom"],
    1   :   ["xenon"],
    2   :   ["krypton"],
    3   :   ["argon"],
    4   :   ["neon"],
}

def setup(settings, *args, **kwargs):
    """
    Creates and returns a plasma object based on settings dictionary passed in.
    The settings parameter must have keys 'neutral_gas' and 'masses'. 'masses'
    must be a dictionary where at least 'm_i' must be defined, 'm_e' may be ommited
    in a custom plasma case. If a known neutral_gas type is choosen such as Xenon, 
    then 'm_i' may be ommitted as well.
    
    Keys:
        'netural_gas'   : str   ->  name of plasma['cylinderical', 'spherical', or 'planar']
        'masses'        : dict  ->  masses of ions and electrons in kg    [{'m_i:<value>, (optional) 'm_e':<value>}]
    (optional)
        'name'      : str   ->  name designation for plasma object
        'amu'       : bool  ->  if True, then m_i and m_e are given in amu instead of kg
        'args'      : tuple ->  addional position arguments
        'kwargs'    : dict  ->  addional keyword arguments

    Returns: Probe Object

    Other Notes:
        mass of an electron is 1/1836 in amu --or-- 5.4466e-4
        """
    shape = settings.pop("neutral_gas").lower()
    if shape in available_plasma_classes[0]:
        Plasma_ = Plasma
    elif shape in available_plasma_classes[1]:
        Plasma_ = XenonPlasma
    elif shape in available_plasma_classes[2]:
        Plasma_ = KryptonPlasma
    elif shape in available_plasma_classes[3]:
        Plasma_ = ArgonPlasma
    elif shape in available_plasma_classes[4]:
        Plasma_ = NeonPlasma
    else:
        raise ValueError("'%s' is not a valid option."%(shape))
    masses = settings["masses"]
    amu = settings.get("amu", False)
    if amu is True:
        settings["m_i"] = (masses["m_i"]*c.m_p if masses["m_i"] is not None else None) if "m_i" in masses else None
        settings["m_e"] = (masses["m_e"]*c.m_p if masses["m_e"] is not None else None) if "m_e" in masses else None
    output: Plasma = object_setup(
        *args,
        settings=settings,
        builders={},
        Builder=Plasma_,
        **kwargs,
    )
    return output


class Plasma:
    def __init__(self, m_i, m_e=c.m_e, neutral_gas=None, name=None,description=None,*args, **kwargs) -> None:
        self._m_i = m_i
        self._m_e = m_e
        self._neutral_gas = neutral_gas
        self._name = name
        self._description = description

    @property
    def m_i(self):
        return self._m_i

    @property
    def m_e(self):
        return self._m_e

    @property
    def neutral_gas(self):
        return self._neutral_gas

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, string):
        if isinstance(string, (str, type(None))):
            self._name = string
        else:
            raise TypeError("'%s' Must be a str or None type, not %s"%(str(string),str(type(string))))
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, string):
        if isinstance(string, (str, type(None))):
            self._description = string
        else:
            raise TypeError("Description change must be str or None type, not type '%s'"%(str(type(string))))


class XenonPlasma(Plasma):
    def __init__(self, m_i=None, m_e=c.m_e, name=None,*args, **kwargs) -> None:
        neutral_gas = "Xenon"
        if m_i is None:
            m_i = 131.29*c.m_p  # amu*kg -> kg
        super().__init__(m_i, m_e, neutral_gas, name, *args, **kwargs)


class ArgonPlasma(Plasma):
    def __init__(self, m_i=None, m_e=c.m_e, name=None, *args, **kwargs) -> None:
        neutral_gas = "Argon"
        if m_i is None:
            m_i = 39.948*c.m_p  # amu*kg -> kg
        super().__init__(m_i, m_e, neutral_gas, name, *args, **kwargs)

class NeonPlasma(Plasma):
    def __init__(self, m_i=None, m_e=c.m_e, name=None, *args, **kwargs) -> None:
        neutral_gas = "Neon"
        if m_i is None:
            m_i = 20.1797*c.m_p  # amu*kg -> kg
        super().__init__(m_i, m_e, neutral_gas, name, *args, **kwargs)

class KryptonPlasma(Plasma):
    def __init__(self, m_i=None, m_e=c.m_e, name=None, *args, **kwargs) -> None:
        neutral_gas = "Krypton"
        if m_i is None:
            m_i = 283.798*c.m_p  # amu*kg -> kg
        super().__init__(m_i, m_e, neutral_gas, name, *args, **kwargs)