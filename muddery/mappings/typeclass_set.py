"""
All available requests.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.utils.utils import classes_in_path, load_modules
from muddery.typeclasses.base_typeclass import BaseTypeclass


class TypeclassSet(object):
    """
    All available typeclasses.
    """
    def __init__(self):
        self.dict = {}
        self.load()

    def load(self):
        """
        Add all typeclasses from the typeclass path.
        """
        for cls in classes_in_path(settings.PATH_TYPECLASSES_BASE, BaseTypeclass):
            key = cls.key

            if not key:
                logger.log_errmsg("Missing typeclass's key.")
                continue

            if self.dict.has_key(key):
                logger.log_infomsg("Typeclass %s is replaced by %s." % (key, cls))

            self.dict[key] = cls
            
        print(self.dict)

    def reload(self):
        """
        Reload typeclasses with correct base class.
        """
        for module in load_modules(settings.PATH_TYPECLASSES_BASE):
            reload(module)

    def get(self, key):
        """
        Get a typeclass.
        """
        return self.dict[key]

    def get_group(self, key):
        """
        Get a typeclass and its all children.
        """
        cls = self.dict[key]
        typeclasses = {key: cls}

        for key in self.dict:
            if is_child(self.dict[key], cls):
                typeclasses[key] = self.dict[key]

        return typeclasses


# Set base typeclasses to default class first.
def TYPECLASS(key):
    return BaseTypeclass

TYPECLASS_SET = TypeclassSet()
TYPECLASS = TYPECLASS_SET.get

# Reload typeclasses with correct base class.
TYPECLASS_SET.reload()


