"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from evennia.utils.utils import lazy_property
from evennia.typeclasses.models import DbHolder
from muddery.server.utils.object_states_handler import ObjectStatesHandler
from muddery.server.dao.properties_dict import PropertiesDict


class BaseComponent(object):
    """
    The base brick.
    """
    element_key = ""
    element_name = ""
    brick_desc = ""

    # object's data model
    model_name = ""

    @classmethod
    def get_models(cls):
        """
        Get this brick's models.
        """
        if "_all_models_" not in cls.__dict__:
            cls._all_models_ = []

            if cls.element_key:
                if not cls.model_name:
                    raise ValueError("%s's model name is empty." % cls.element_key)

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

            if cls.element_key:
                for c in cls.__bases__:
                    if hasattr(c, "get_properties_info"):
                        cls._all_properties_.update(c.get_properties_info())

                records = PropertiesDict.get_properties(cls.element_key)
                for record in records:
                    cls._all_properties_[record.property] = {"name": record.name,
                                                             "desc": record.desc,
                                                             "default": record.default,
                                                             "mutable": record.mutable,}

        return cls._all_properties_

    @lazy_property
    def states_handler(self):
        return ObjectStatesHandler(self.get_type(), self.get_id())

    # @property state stores object's running state.
    def __state_get(self):
        """
        A non-attr_obj store (ndb: NonDataBase). Everything stored
        to this is guaranteed to be cleared when a server is shutdown.
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.ndb.attr = value etc.
        """
        return self.states_handler

    # @state.setter
    def __state_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to ndb object! "
        string += "Use self.state.name=value instead."
        raise Exception(string)

    # @state.deleter
    def __state_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the state object!")

    state = property(__state_get, __state_set, __state_del)

    def get_type(self):
        """
        Get the object's type.

        :return: (string) object's type
        """
        return self.element_key

    def get_id(self):
        """
        Get the object's id.

        :return: (number) object's id
        """
        return 0
