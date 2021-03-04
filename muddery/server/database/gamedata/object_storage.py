"""
Object's attributes cache.
"""

import json, traceback
from collections import OrderedDict, deque
from django.apps import apps
from django.conf import settings
from evennia.accounts.models import AccountDB
from evennia.comms.models import ChannelDB
from evennia.objects.models import ObjectDB
from evennia.scripts.models import ScriptDB
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.database.storage.kv_table import KeyValueTable


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
    elif issubclass(type(value), ObjectDB):
        str_value = json.dumps((value.id, "ObjectDB"))
    elif issubclass(type(value), ScriptDB):
        str_value = json.dumps((value.id, "ScriptDB"))
    elif issubclass(type(value), AccountDB):
        str_value = json.dumps((value.id, "AccountDB"))
    elif issubclass(type(value), ChannelDB):
        str_value = json.dumps((value.id, "ChannelDB"))
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
        elif data_type in {"ObjectDB", "ScriptDB", "AccountDB", "ChannelDB"}:
            model = eval(data_type)
            value = model.objects.get(id=json_value)
        elif data_type in {"dict", "OrderedDict"}:
            value = eval(data_type)((from_string(key), from_string(item)) for key, item in json_value.items())
        else:
            value = eval(data_type)(from_string(item) for item in json_value)
    except Exception as e:
        raise MudderyError(ERR.server_error, "The object can not load %s." % str_value)

    return value


def delete_string(str_value):
    # delete the string's object
    try:
        json_value, data_type = json.loads(str_value)
        if data_type == "NoneType":
            pass
        elif data_type in {"str", "int", "float", "bool", "bytes"}:
            pass
        elif data_type in ("ObjectDB", "ScriptDB", "AccountDB", "ChannelDB"):
            model = eval(data_type)
            value = model.objects.get(id=json_value)
            value.delete()
        elif data_type in ("dict", "OrderedDict"):
            for value in json_value.values():
                delete_string(value)
        else:
            for item in json_value:
                delete_string(item)
    except Exception as e:
        traceback.print_exc()
        raise MudderyError(ERR.server_error, "Can not delete object %s: %s" % (str_value, e))

    return


class ObjectStorage(object):
    """
    The storage of object attributes.
    """
    def __init__(self, model_name, obj_id_column=None):
        # db model
        self.storage = KeyValueTable(model_name, obj_id_column)

    def save(self, obj_id, key, value):
        """
        Set an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            value: (any) attribute's value.
        """
        str_value = to_string(value)
        self.storage.save(obj_id, key, str_value)

    def saves(self, obj_id, value_dict):
        """
        Set attributes.

        Args:
            obj_id: (number) object's id.
            value_dict: (dict) a dict of key-values.
        """
        str_value_dict = {key: to_string(value) for key, value in value_dict.items()}
        self.storage.saves(obj_id, str_value_dict)

    def has(self, obj_id, key):
        """
        Check if the attribute exists.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        return self.storage.has(obj_id, key)

    def load(self, obj_id, key, *default):
        """
        Get the value of an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            default: (any or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        try:
            value = self.storage.load(obj_id, key)
            return from_string(value)
        except AttributeError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e

    def load_obj(self, obj_id):
        """
        Get values of an object.

        Args:
            obj_id: (number) object's id.
        """
        values = self.storage.load_category(obj_id)
        return {key: from_string(value) for key, value in values.items()}

    def delete(self, obj_id, key):
        """
        delete an attribute of an object.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        values = self.storage.delete(obj_id, key)
        for value in values:
            delete_string(value)

    def remove_obj(self, obj_id):
        """
        Remove an object's all attributes.

        Args:
            obj_id: (number) object's id.
        """
        values = self.storage.delete_category(obj_id)
        for value in values:
            delete_string(value)

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        return self.storage.atomic()
