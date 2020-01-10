from abc import ABC, abstractmethod
from collections import namedtuple


class Split(ABC, namedtuple('_Split', ['id','tty', 'display', 'settings'])):
    """Represents a split capable of displaying information.
    Must be copyable without sideeffects"""
    @abstractmethod
    def size(self):
        pass
