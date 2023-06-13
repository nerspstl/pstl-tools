from pstl.utls import constants as c


class Plasma:
    def __init__(self, m_i, m_e=c.m_e, gas=None, *args, **kwargs) -> None:
        self._m_i = m_i
        self._m_e = m_e
        self._gas = gas

    @property
    def m_i(self):
        return self._m_i

    @property
    def m_e(self):
        return self._m_e

    @property
    def gas(self):
        return self._gas


class XenonPlasma(Plasma):
    def __init__(self, m_i=None, m_e=c.m_e, gas=None, *args, **kwargs) -> None:
        if m_i is None:
            m_i = 131.29*c.m_p  # amu*kg -> kg
        super().__init__(m_i, m_e, gas, *args, **kwargs)


class ArgonPlasma(Plasma):
    def __init__(self, m_i=None, m_e=c.m_e, gas=None, *args, **kwargs) -> None:
        if m_i is None:
            m_i = 39.948*c.m_p  # amu*kg -> kg
        super().__init__(m_i, m_e, gas, *args, **kwargs)
