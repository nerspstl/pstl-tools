from abc import ABC, abstractmethod

import numpy as np


from pstl.utls.objects import setup as object_setup
from pstl.diagnostics.probes.classes import Probe

available_probe_classes = [
    ["4grid", "four", "fourgrid"],
    [ "3grid", "three","threegrid"],
]

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
