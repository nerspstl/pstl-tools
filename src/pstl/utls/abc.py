from abc import ABC, abstractmethod, abstractproperty

class PSTLObject(ABC):
    def __init__(self) -> None:
        super().__init__()

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