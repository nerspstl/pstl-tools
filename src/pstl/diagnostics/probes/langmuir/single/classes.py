from abc import ABC, abstractmethod, abstractproperty

import numpy as np

from pstl.diagnostics.probes.classes import Probe

available_probe_classes = [
    ["cylinderical"],
    ["spherical"],
    ["planer", "planar"],
]

def setup(settings):
    """
    Creates and returns a Langmuir probe object  based on settings dictionary passed in.
    The settings parameter must have keys 'shape' and 'dimensions'.
    
    Keys:
        'shape'     : str   ->  geometery shape of probe ['cylinderical', 'spherical', or 'planar']
        'dimensions': dict  ->  probe dimensions    [{'diameter':<value>,'length':<value>}]
    (optional)
        'name'      : str   ->  name designation for probe 
        'args'      : tuple ->  addional position arguments
        'kwargs'    : dict  ->  addional keyword arguments

    Returns: Probe Object
        """
    shape = settings["shape"].lower()
    if shape in available_probe_classes[0]:
        Probe = CylindericalSingleProbeLangmuir
    elif shape in available_probe_classes[1]:
        Probe = SphericalSingleProbeLangmuir
    elif shape in available_probe_classes[2]:
        Probe = PlanarSingleProbeLangmuir
    else:
        raise ValueError("'%s' is not a valid option."%(shape))
    name = settings.get("name",None)
    description = settings.get("description",None)
    dimensions = settings["dimensions"]
    args = settings.get("args", (None))
    kwargs = settings.get("kwargs",{})
    kwargs["name"] = kwargs.get("name","") if name is None else name
    kwargs["description"] = kwargs.get("description","") if description is None else description
    probe = Probe(*args,**dimensions,**kwargs)
    return probe

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
