from abc import ABC, abstractmethod

import numpy as np


from pstl.utls.objects import setup as object_setup
from pstl.diagnostics.probes.classes import Probe

available_probe_classes = [
    [4, "4grid", "four", "fourgrid"],
    [ 3, "3grid", "three","threegrid"],
]

def setup(settings, *args, **kwargs):
    """
    Creates and returns a RPA probe object  based on settings dictionary passed in.
    The settings parameter must have keys 'ngrids'.
    
    Keys:
        'ngrids'     : int   ->  number of grids [4,3]
    (optional)
        'name'      : str   ->  name designation for probe 
        'args'      : tuple ->  addional position arguments
        'kwargs'    : dict  ->  addional keyword arguments

    Returns: Probe Object
    """
    # determine shape of 
    shape = settings.pop("ngrids").lower()
    if shape in available_probe_classes[0]:
        Probe = FourGridRPA
    elif shape in available_probe_classes[1]:
        Probe = ThreeGridRPA
    else:
        raise ValueError("'%s' is not a valid option."%(shape))
    
    output_object: RepellingPotentialAnalyzer = object_setup(
        *args,
        settings=settings,
        builders={},
        Builder=Probe,
    #    to_args=
        **kwargs,
    )

    return output_object

class RepellingPotentialAnalyzer(Probe, ABC):
    def __init__(self, *args, ngrids: int | None = None, name=None, description=None, **kwargs) -> None:
        # *args should be the potentials of the grids
        # need to add something for space between grids & collection area 
        # to determine resounce times
        self._ngrids = int(ngrids) if ngrids is not None else int(len(args))

    @property
    def ngrids(self):
        return self._ngrids
    

class FourGridRPA(RepellingPotentialAnalyzer):
    def __init__(self, *args, name=None, description=None, **kwargs) -> None:
        ngrids = 4
        super().__init__(*args, ngrids=ngrids, name=name, description=description, **kwargs)

class ThreeGridRPA(RepellingPotentialAnalyzer):
    def __init__(self, *args, name=None, description=None, **kwargs) -> None:
        ngrids = 3
        super().__init__(*args, ngrids=ngrids, name=name, description=description, **kwargs)

class RPA(RepellingPotentialAnalyzer):
    def __init__(self, *args, ngrids: int | None = None, name=None, description=None, **kwargs) -> None:
        super().__init__(*args, ngrids=ngrids, name=name, description=description, **kwargs)
