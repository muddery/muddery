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
            cls.__all_models__ = set()
            classes = cls.__bases__
            for c in classes:
                if hasattr(c, "get_models"):
                    cls.__all_models__ |= c.get_models()

            if cls.model_name:
                cls.__all_models__.add(cls.model_name)

        return cls.__all_models__
