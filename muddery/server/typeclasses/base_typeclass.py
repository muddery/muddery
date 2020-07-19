"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from muddery.server.dao.properties_dict import PropertiesDict


class BaseTypeclass(object):
    """
    This base typeclass.
    """
    typeclass_key = ""
    typeclass_name = ""
    typeclass_desc = ""

    # object's data model
    model_name = ""

    # objects states
    states = set()

    @classmethod
    def get_models(cls):
        """
        Get this typeclass's models.
        """
        if "_all_models_" not in cls.__dict__:
            cls._all_models_ = []

            if cls.typeclass_key:
                if not cls.model_name:
                    raise ValueError("%s's model name is empty." % cls.typeclass_key)

                for c in cls.__bases__:
                    if hasattr(c, "get_models"):
                        cls._all_models_.extend(c.get_models())

                if cls.model_name not in cls._all_models_:
                    cls._all_models_.append(cls.model_name)

        return cls._all_models_

    @classmethod
    def get_properties_info(cls):
        """
        Get this typeclass's models.
        """
        if "_all_properties_" not in cls.__dict__:
            cls._all_properties_ = {}

            if cls.typeclass_key:
                for c in cls.__bases__:
                    if hasattr(c, "get_properties_info"):
                        cls._all_properties_.update(c.get_properties_info())

                records = PropertiesDict.get_properties(cls.typeclass_key)
                for record in records:
                    cls._all_properties_[record.property] = {"name": record.name,
                                                             "desc": record.desc,
                                                             "default": record.default,
                                                             "mutable": record.mutable,}

        return cls._all_properties_
