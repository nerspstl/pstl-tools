from abc import ABC, abstractmethod, abstractproperty

import numpy as np

from pstl.diagnostics.probes.classes import Probe

available_plasma_properties = [
    "V_f",
    "V_s",
    "KT_e",
    "lambda_De",
    "n_e",
    "n_i",
    "I_es",
    "I_is",
    "J_es",
    "J_is",
    "sheath",
]


class SingleProbeLangmuir(Probe, ABC):
    def __init__(self, diameter, *args, shape="Unknown", **kwargs) -> None:
        self._diameter = float(diameter)
        self._radius = diameter/2
        self._shape = shape

        self._area = self.calc_area(diameter, *args, **kwargs)

    @property
    def diameter(self):
        return self._diameter

    @property
    def radius(self):
        return self._radius

    @property
    def area(self):
        return self._area

    @property
    def shape(self):
        return self._shape

    @abstractmethod
    def calc_area(self, diameter, *args, **kwargs) -> float:
        pass


class CylindericalSingleProbeLangmuir(SingleProbeLangmuir):
    def __init__(self, diameter, length, *args, **kwargs) -> None:
        shape = "cylinderical"
        super().__init__(diameter, length, *args, shape=shape, **kwargs)

        self._length = float(length)

    @property
    def length(self):
        return self._length

    def calc_area(self, diameter, length, *args, **kwargs) -> float:
        super().calc_area(diameter, length, *args, **kwargs)
        return diameter*np.pi*(length + diameter/4)


class PlanarSingleProbeLangmuir(SingleProbeLangmuir):
    def __init__(self, diameter, *args, **kwargs) -> None:
        shape = "planar"
        super().__init__(diameter, *args, shape=shape, **kwargs)

    def calc_area(self, diameter, *args, **kwargs) -> float:
        super().calc_area(diameter, *args, **kwargs)
        return diameter*diameter*np.pi/4


class SphericalSingleProbeLangmuir(SingleProbeLangmuir):
    def __init__(self, diameter, length=None, *args, **kwargs) -> None:
        if length is None:
            length = diameter

        shape = "spherical"
        super().__init__(diameter, length, *args, shape=shape, **kwargs)

        self._length = float(length)

    @property
    def length(self):
        return self._length

    def calc_area(self, diameter, length, *args, **kwargs) -> float:
        super().calc_area(diameter, length, *args, **kwargs)
        height = length-diameter/2
        radius = diameter/2
        cap = 2*np.pi*(radius*height)
        hemisphere = 2*np.pi*radius*radius
        return cap+hemisphere
