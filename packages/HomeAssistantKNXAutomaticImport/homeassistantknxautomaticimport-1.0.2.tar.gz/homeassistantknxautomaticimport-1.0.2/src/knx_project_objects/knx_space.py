from __future__ import annotations  # Enables forward references in type hints

from unidecode import unidecode

from xknxproject.models import Space

from classfromtypeddict import ClassFromTypedDict

class KNXSpace(ClassFromTypedDict):
    _class_ref = Space

    # for information, instance attributes
    # warning: used ClassFromTypedDict below needs
    #   to be import otherwise the conversion does not work
    # spaces : dict[str, KNXSpace]
    # functions : list[str]

    def __init__(self, data: dict):
        self._name = ""
        self.spaces : dict[str, KNXSpace] = {}
        self.functions : list[str] = []
        super().__init__(data)

    @property
    def name(self):
        return unidecode(self._name)

    @name.setter
    def name(self, string: str):
        self._name = string

    @property
    def flat_name(self):
        return self.name.lower()
