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

    @classmethod
    def get_properties_info(cls):
        """
        Get this typeclass's models.
        """
        if "_all_properties_" not in cls.__dict__:
            cls._all_properties_ = {}
            for c in cls.__bases__:
                if hasattr(c, "get_properties_info"):
                    cls._all_properties_.update(c.get_properties_info())

            from muddery.worlddata.dao.properties_dict_mapper import PROPERTIES_DICT
            records = PROPERTIES_DICT.get_properties(cls.typeclass_key)
            for record in records:
                added = False
                for info in cls._all_properties_:
                    if info["key"] == record.key:
                        added = True
                        break
                if added:
                    continue

                if not record.key in cls._all_properties_:
                    cls._all_properties_[record.key] = {"name": record.name,
                                                        "desc": record.desc,
                                                        "mutable": record.mutable}

        return cls._all_properties_
