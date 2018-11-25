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

    @classmethod
    def get_models(cls):
        """
        Get this typeclass's models.
        """
        if "_all_models_" not in cls.__dict__:
            cls._all_models_ = []
            for c in cls.__bases__:
                if hasattr(c, "get_models"):
                    cls._all_models_.extend(c.get_models())

            if cls.model_name and not cls.model_name in cls._all_models_:
                cls._all_models_.append(cls.model_name)

        return cls._all_models_
