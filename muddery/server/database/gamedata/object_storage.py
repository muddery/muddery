"""
Object's attributes cache.
"""

import json
from collections import OrderedDict
from django.conf import settings
from muddery.server.utils import utils
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.database.storage.memory_storage import MemoryStorage


def to_string(value):
    # pack a value to a string.
    data_type = type(value)
    if value is None:
        # inner types
        str_value = json.dumps((value, data_type.__name__))
    elif data_type in {str, int, float, bool, bytes}:
        # inner types
        str_value = json.dumps((value, data_type.__name__))
    elif hasattr(value, "__iter__"):
        # iterable value
        if data_type in {dict, OrderedDict}:
            str_value = json.dumps((dict((to_string(key), to_string(obj)) for key, obj in value.items()), data_type.__name__))
        else:
            try:
                str_value = json.dumps((tuple(to_string(obj) for obj in value), data_type.__name__))
            except Exception as e:
                raise MudderyError(ERR.server_error, "The object could not be stored.")
    else:
        raise MudderyError(ERR.server_error, "The object can not store %s of %s." % (value, type(value)))

    return str_value


def from_string(str_value):
    # unpack a value from a string.
    if str_value is None:
        return None

    try:
        json_value, data_type = json.loads(str_value)
        if data_type == "NoneType":
            value = None
        elif data_type in {"str", "int", "float", "bool", "bytes"}:
            value = eval(data_type)(json_value)
        elif data_type in {"dict", "OrderedDict"}:
            value = eval(data_type)((from_string(key), from_string(item)) for key, item in json_value.items())
        else:
            value = eval(data_type)(from_string(item) for item in json_value)
    except Exception as e:
        raise MudderyError(ERR.server_error, "The object can not load %s." % str_value)

    return value


class BaseObjectStorage(object):
    """
    The storage of object attributes.
    """
    # data storage
    storage_class = None
    storage = None

    @classmethod
    def save(cls, obj_id, key, value):
        """
        Set an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            value: (any) attribute's value.
        """
        to_save = to_string(value)
        cls.storage.save(obj_id, key, to_save)

    @classmethod
    def save_keys(cls, obj_id, value_dict):
        """
        Set attributes.

        Args:
            obj_id: (number) object's id.
            value_dict: (dict) a dict of key-values.
        """
        if value_dict:
            with cls.storage.atomic():
                for key, value in value_dict.items():
                    cls.storage.save(obj_id, key, to_string(value))

    @classmethod
    def has(cls, obj_id, key):
        """
        Check if the attribute exists.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        return cls.storage.has(obj_id, key)

    @classmethod
    def load(cls, obj_id, key, *default):
        """
        Get the value of an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        try:
            value = cls.storage.load(obj_id, key)
            return from_string(value)
        except KeyError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e

    @classmethod
    def load_obj(cls, obj_id):
        """
        Get values of an object.

        Args:
            obj_id: (number) object's id.
        """
        values = cls.storage.load_category(obj_id, {})
        return {key: from_string(value) for key, value in values.items()}

    @classmethod
    def delete(cls, obj_id, key):
        """
        delete an attribute of an object.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        cls.storage.delete(obj_id, key)

    @classmethod
    def remove_obj(cls, obj_id):
        """
        Remove an object's all attributes.

        Args:
            obj_id: (number) object's id.
        """
        cls.storage.delete_category(obj_id)

    @classmethod
    def atomic(cls):
        """
        Guarantee the atomic execution of a given block.
        """
        return cls.storage.atomic()


class DBObjectStorage(BaseObjectStorage):
    """
    The storage of object attributes.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    session = settings.GAME_DATA_APP
    config = settings.AL_DATABASES[session]
    storage = storage_class(session, config["MODELS"], "object_states", "obj_id", "key", "value")


class MemoryObjectStorage(BaseObjectStorage):
    """
    The storage of object attributes.
    """
    # data storage
    storage_class = MemoryStorage
    storage = storage_class()
