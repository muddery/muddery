"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

import ast
from evennia.utils import logger
from evennia.utils.utils import lazy_property
from muddery.server.utils.data_field_handler import DataFieldHandler, ConstDataHolder
from muddery.server.utils.object_states_handler import ObjectStatesHandler
from muddery.server.database.worlddata.properties_dict import PropertiesDict
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.object_properties import ObjectProperties


class BaseElement(object):
    """
    The base brick.
    """
    element_type = ""
    element_name = ""
    brick_desc = ""

    # object's data model
    model_name = ""

    def __init__(self, *agrs, **wargs):
        super(BaseElement, self).__init__(*agrs, **wargs)
        self.element_key = ""
        self.level = 0

    @classmethod
    def get_models(cls):
        """
        Get this brick's models.
        """
        if "_all_models_" not in cls.__dict__:
            cls._all_models_ = []

            if cls.element_type:
                if not cls.model_name:
                    raise ValueError("%s's model name is empty." % cls.element_type)

                for c in cls.__bases__:
                    if hasattr(c, "get_models"):
                        cls._all_models_.extend(c.get_models())

                if cls.model_name not in cls._all_models_:
                    cls._all_models_.append(cls.model_name)

        return cls._all_models_

    @classmethod
    def get_properties_info(cls):
        """
        Get object's custom properties.
        """
        if "_all_properties_" not in cls.__dict__:
            cls._all_properties_ = {}

            if cls.element_type:
                for c in cls.__bases__:
                    if hasattr(c, "get_properties_info"):
                        cls._all_properties_.update(c.get_properties_info())

                records = PropertiesDict.get_properties(cls.element_type)
                for record in records:
                    cls._all_properties_[record.property] = {"name": record.name,
                                                             "desc": record.desc,
                                                             "default": record.default,
                                                             "mutable": record.mutable,}

        return cls._all_properties_

    @lazy_property
    def const_data_handler(self):
        return DataFieldHandler(self)

    # @property system stores object's data.
    def __const_get(self):
        """
        A system_data store. Everything stored to this is from the
        world data. It will be reset every time when the object init .
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.system.attr = value etc.
        """
        try:
            return self._const_data_holder
        except AttributeError:
            self._const_data_holder = ConstDataHolder(self, "system_data", manager_name='const_data_handler')
            return self._const_data_holder

    # @data.setter
    def __const_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to data object! "
        raise Exception(string)

    # @data.deleter
    def __const_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the system data object!")
    const = property(__const_get, __const_set, __const_del)

    @lazy_property
    def states(self):
        return ObjectStatesHandler(self)

    def get_type(self):
        """
        Get the object's type.

        :return: (string) object's type
        """
        return self.element_type

    def is_element(self, element_type):
        """
        Is a subclass of the element type.
        :param element_type:
        :return:
        """
        return isinstance(self, ELEMENT(element_type))

    def set_element_key(self, key):
        """
        Set element data's key.

        Args:
            key: (string) Key of the data.
        """
        self.element_key = key

        if self.model_name:
            # Load data.
            try:
                # Load db data.
                self.load_data(self.model_name, key)
            except Exception as e:
                logger.log_errmsg("%s %s can not load data:%s" % (self.model_name, key, e))

        self.after_data_loaded()

    def load_data(self, model, key):
        """
        Get object's data from database.

        Args:
            model: (String) data's table name.
            key: (String) object's data key.

        Returns:
            None
        """
        # Get data record.
        try:
            fields = WorldData.get_fields(model)
            record = WorldData.get_table_data(model, key=key)
            record = record[0]
        except Exception as e:
            logger.log_errmsg("Can not find key %s in %s" % (key, model))
            return

        # Set data.
        for field_name in fields:
            self.const_data_handler.add(field_name, getattr(record, field_name))

    def set_level(self, level):
        """
        Set element's level.
        :param level:
        :return:
        """
        self.level = level
        self.load_custom_level_data(level)

    def load_custom_level_data(self, level):
        # Get custom data.
        values = {}
        for record in ObjectProperties.get_properties(self.element_key, level):
            key = record.property
            serializable_value = record.value
            if serializable_value == "":
                value = None
            else:
                try:
                    value = ast.literal_eval(serializable_value)
                except (SyntaxError, ValueError) as e:
                    # treat as a raw string
                    value = serializable_value
            values[key] = value

        # Set values.
        for key, info in self.get_properties_info().items():
            self.const_data_handler.add(key, values.get(key, ast.literal_eval(info["default"])))

    def after_data_loaded(self):
        """
        Called after self.load_data().
        """
        pass

    def get_element_key(self):
        """
        Get element key.
        :return:
        """
        return self.element_key
