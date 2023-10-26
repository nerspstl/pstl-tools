from abc import ABC, abstractmethod

import numpy as np

class Probe(ABC):
    def __init__(self,name=None, description=None) -> None:
        super().__init__()
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, string):
        if isinstance(string, (str, type(None))):
            self._name = string
        else:
            raise TypeError("Name change must be str or None type, not type '%s'"%(str(type(string))))

    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, string):
        if isinstance(string, (str, type(None))):
            self._description = string
        else:
            raise TypeError("Description change must be str or None type, not type '%s'"%(str(type(string))))
    