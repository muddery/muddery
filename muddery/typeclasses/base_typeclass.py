"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from __future__ import print_function

class BaseTypeclass(object):
    """
    This base typeclass.
    """
    typeclass_key = ""
    typeclass_name = ""
    typeclass_desc = ""
    model_name = ""
    __all_models__ = None

    @classmethod
    def get_models(cls):
        """
        Get this typeclass's models.
        """
        if cls.__all_models__ is None:
            cls.__all_models__ = []
            for c in cls.__bases__:
                if hasattr(c, "get_models"):
                    cls.__all_models__.extend(c.get_models())

            if cls.model_name and not cls.model_name in cls.__all_models__:
                cls.__all_models__.append(cls.model_name)

        return cls.__all_models__
