"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

import ast
from evennia.utils import logger
from evennia.utils.utils import lazy_property
from muddery.server.utils.data_field_handler import DataFieldHandler, ConstDataHolder
from muddery.server.database.worlddata.properties_dict import PropertiesDict
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.element_properties import ElementProperties


class BaseElement(object):
    """
    The base brick.
    """
    element_type = ""
    element_name = ""

    # object's data model
    model_name = ""

    def __init__(self, *agrs, **wargs):
        super(BaseElement, self).__init__(*agrs, **wargs)
        self.element_key = ""
        self.level = None

        # is temporary element.
        self.is_temp = False

    @classmethod
    def get_base_model(cls):
        """
        Get this element's root base class's model.
        """
        if "_base_model_" in cls.__dict__:
            return cls._base_model_

        cls._base_model_ = ""

        if cls.element_type:
            for c in cls.__bases__:
                if hasattr(c, "get_base_model"):
                    base_model = c.get_base_model()
                    if base_model:
                        cls._base_model_ = base_model
                        break

        if not cls._base_model_ and cls.model_name:
            cls._base_model_ = cls.model_name

        return cls._base_model_

    @classmethod
    def get_models(cls):
        """
        Get this element and all its base class's models.
        """
        if "_all_models_" not in cls.__dict__:
            cls._all_models_ = []

            if cls.element_type:
                for c in cls.__bases__:
                    if hasattr(c, "get_models"):
                        cls._all_models_.extend(c.get_models())

                if cls.model_name and cls.model_name not in cls._all_models_:
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
                    cls._all_properties_[record.property] = {
                        "name": record.name,
                        "desc": record.desc,
                        "default": record.default,
                    }

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

    def at_creation(self):
        """
        Called once, when this object is first created..
        """
        pass

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

    def setup_element(self, key, level=None, first_time=False, temp=False):
        """
        Set element data's key.

        Args:
            key: (string) the key of the data.
            level: (int) element's level.
            first_time: (bool) the first time to setup the element.
            temp: (bool) template element.
        """
        self.element_key = key
        self.level = level
        self.is_temp = temp

        self.load_data(key, level)

        self.at_element_setup(first_time)

        self.after_element_setup(first_time)

    def load_data(self, key, level=None):
        """
        Load the object's data.

        :arg
            key: (string) the key of the data.
            level: (int) element's level.

        :return:
        """
        # Load data.
        try:
            # Load db data.
            base_model = self.get_base_model()
            self.load_base_data(base_model, key)

            # reset element type
            if self.const_data_handler.has("element_type"):
                if self.const.element_type:
                    self.set_element_type(self.const.element_type)
                else:
                    logger.log_errmsg("%s does not have element type." % key)

            # Load extend data.
            self.load_extend_data(base_model, key)
        except Exception as e:
            logger.log_errmsg("%s %s can not load data:%s" % (self.model_name, key, e))

        self.load_custom_level_data(level)

    def load_base_data(self, model, key):
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

    def load_extend_data(self, base_model, key):
        """
        Get object's extend data from database except base data.

        Args:
            base_model: (String) base data's table name.
            key: (String) object's data key.

        Returns:
            None
        """
        # Get models.
        for data_model in self.get_models():
            if data_model == base_model:
                continue

            # Get data record.
            try:
                fields = WorldData.get_fields(data_model)
                record = WorldData.get_table_data(data_model, key=key)
                record = record[0]
            except Exception as e:
                logger.log_errmsg("Can not find key %s in %s" % (key, data_model))
                continue

            # Set data.
            for field_name in fields:
                self.const_data_handler.add(field_name, getattr(record, field_name))

    def set_element_type(self, element_type):
        """
        Set object's type.

        Args:
            element_type: (string) Element's type.
        """
        new_class = ELEMENT(element_type)
        if not new_class:
            logger.log_errmsg("Can not get the element type: %s." % element_type)
            return

        if type(self) == new_class:
            # No change.
            return

        # Set new class.
        self.__class__ = new_class
        if self.element_type != element_type:
            logger.log_errmsg("Element type %s is wrong!" % element_type)
            return

    def set_level(self, level):
        """
        Set element's level.
        :param level:
        :return:
        """
        self.level = level
        self.load_custom_level_data(level)

    def get_level(self):
        """
        Get the elemet's level.
        :return:
        """
        return self.level

    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        level = self.get_level()
        self.set_level(level + 1)

    def load_custom_level_data(self, level):
        """
        Load custom's level data.

        :param level:
        :return:
        """
        # Get custom data.
        values = {}
        for record in ElementProperties.get_properties(self.element_type, self.element_key, level):
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
            if key in values:
                # direct value
                value = values.get(key)
            elif info["default"] in values:
                # Get default value.
                # the value of another value
                value = values.get(info["default"])
            elif self.const_data_handler.has(info["default"]):
                # the value of another const
                value = self.const_data_handler.get(info["default"])
            else:
                try:
                    value = ast.literal_eval(info["default"])
                except (SyntaxError, ValueError) as e:
                    # treat as a raw string
                    value = info["default"]

            self.const_data_handler.add(key, value)

    def at_element_setup(self, first_time):
        """
        Called when the element is setting up.

        :arg
            first_time: (bool) the first time to setup the element.
        """
        pass

    def after_element_setup(self, first_time):
        """
        Called after the element is setting up.

        :arg
            first_time: (bool) the first time to setup the element.
        """
        pass

    def at_delete(self):
        """
        Called just before this object is deleted.
        :return:
        """
        pass

    def get_element_key(self):
        """
        Get element key.
        :return:
        """
        return self.element_key
