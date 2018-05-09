"""
All available requests.
"""

from __future__ import print_function

from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.utils.utils import is_child


def typeclass_mapping(key, name=None, desc=None):
    """
    A decorator which add a typeclass to the public typeclass set.

    Args:
        key: (string) the key of the typeclass.
        name: (string, optional) the readable name of the typeclass.
        desc: (string, opitonal) the discripion of the typeclass.
    """
    def wrapper(cls):
        """
        Args:
            cls: (class) a typeclass.
        """
        TYPECLASS_SET.add(cls, key, name, desc)
        return cls

    return wrapper


class TypeclassSet(object):
    """
    All available typeclasses.
    """
    def __init__(self):
        self.dict = {}
        
    def add(self, cls, key, name="", desc=""):
        """
        Add a typeclass.

        Args:
            cls: (class) typeclass.
            key: (string) the key of the typeclass.
        """
        if not key:
            raise MudderyError("Need typeclass's key.")

        if self.dict.has_key(key):
            logger.log_infomsg("Typeclass %s is replaced with %s.", (key, cls))

        self.dict[key] = {
            "cls": cls,
            "name": name,
            "desc": desc,
        }

    def get(self, typeclass_key):
        """
        Get a typeclass.
        """
        return self.dict[typeclass_key]

    def cls(self, typeclass_key):
        return self.dict[typeclass_key]["cls"]

    def get_group(self, typeclass_key):
        """
        Get a typeclass and its all children.
        """
        typeclass = self.dict[typeclass_key]
        typeclasses = {typeclass_key: typeclass}

        cls = typeclass["cls"]
        for key in self.dict:
            if is_child(self.dict[key]["cls"], cls):
                typeclasses[key] = self.dict[key]

        return typeclass


TYPECLASS_SET = TypeclassSet()
TYPECLASS = TYPECLASS_SET.cls

