"""
Object's attributes cache.
"""

import json
import traceback
from collections import OrderedDict
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.database.storage.memory_kv_storage import MemoryKVStorage
from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


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


class BaseObjectStorage(BaseData, Singleton):
    """
    The storage of object attributes.
    """

    # data storage
    async def save(self, obj_id, key, value):
        """
        Set an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            value: (any) attribute's value.
        """
        to_save = to_string(value)
        await self.storage.save(obj_id, key, to_save)

    async def save_keys(self, obj_id, value_dict):
        """
        Set attributes.

        Args:
            obj_id: (number) object's id.
            value_dict: (dict) a dict of key-values.
        """
        if value_dict:
            try:
                with self.storage.transaction():
                    for key, value in value_dict.items():
                        await self.storage.save(obj_id, key, to_string(value))
            except Exception as e:
                traceback.print_exc()

    async def has(self, obj_id, key):
        """
        Check if the attribute exists.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        return await self.storage.has(obj_id, key)

    async def load(self, obj_id, key, *default):
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
            value = await self.storage.load(obj_id, key)
            return from_string(value)
        except KeyError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e

    async def load_obj(self, obj_id):
        """
        Get values of an object.

        Args:
            obj_id: (number) object's id.
        """
        values = await self.storage.load_category(obj_id, {})
        return {key: from_string(value) for key, value in values.items()}

    async def delete(self, obj_id, key):
        """
        delete an attribute of an object.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        await self.storage.delete(obj_id, key)

    async def remove_obj(self, obj_id):
        """
        Remove an object's all attributes.

        Args:
            obj_id: (number) object's id.
        """
        await self.storage.delete_category(obj_id)


class DBObjectStorage(BaseObjectStorage):
    """
    The storage of object attributes.
    """
    __table_name = "object_states"
    __category_name = "obj_id"
    __key_field = "key"
    __default_value_field = "value"

    def __init__(self):
        # data storage
        super(DBObjectStorage, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)


class MemoryObjectStorage(BaseObjectStorage):
    """
    The storage of object attributes.
    """
    def __init__(self):
        # data storage
        super(MemoryObjectStorage, self).__init__()
        self.storage = MemoryKVStorage()
