from pstl.utls import constants as c


class Plasma:
    def __init__(self, m_i, m_e=c.m_e, neutral_gas=None, name=None,*args, **kwargs) -> None:
        self._m_i = m_i
        self._m_e = m_e
        self._neutral_gas = neutral_gas
        self._name = name

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
        if isinstance(string, str):
            self._name = string
        else:
            raise TypeError("'%s' Must be a str type, not %s"%(str(string),str(type(string))))


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