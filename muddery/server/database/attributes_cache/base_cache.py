"""
Object's attributes cache.
"""

import json
from collections import OrderedDict, deque
from django.apps import apps
from django.conf import settings
from evennia.accounts.models import AccountDB
from evennia.comms.models import ChannelDB
from evennia.objects.models import ObjectDB
from evennia.scripts.models import ScriptDB
from muddery.server.utils.exception import MudderyError, ERR


def to_string(value):
    # pack a value to a string.
    data_type = type(value)
    if data_type in (str, int, float, bool, bytes):
        # inner types
        str_value = json.dumps((value, data_type.__name__))
    elif hasattr(value, "__iter__"):
        # iterable value
        if data_type in (dict, OrderedDict):
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
    try:
        json_value, data_type = json.loads(str_value)
        if data_type in ("str", "int", "float", "bool", "bytes"):
            value = eval(data_type)(json_value)
        elif data_type in ("ObjectDB", "ScriptDB", "AccountDB", "ChannelDB"):
            model = eval(data_type)
            value = model.objects.get(id=json_value)
        elif data_type in ("dict", "OrderedDict"):
            value = eval(data_type)((from_string(key), from_string(item)) for key, item in json_value)
        else:
            value = eval(data_type)(from_string(item) for item in json_value)
    except Exception as e:
        raise MudderyError(ERR.server_error, "The object can not load %s." % str_value)

    return value


class BaseAttributesCache(object):
    """
    Object's attributes cache.
    """

    def __init__(self, model_name):
        # db model
        self.model = apps.get_model(settings.GAME_DATA_APP, model_name)

    def set(self, obj_id, key, value):
        """
        Set an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            value: (any) attribute's value.
        """
        str_value = to_string(value)
        records = self.model.objects.filter(obj_id=obj_id, key=key)
        if len(records) == 0:
            record = {
                "obj_id": obj_id,
                "key": key,
                "value": str_value,
            }
            data = self.model(**record)
            data.full_clean()
            data.save()
        else:
            records.update(value=str_value)
        
    def has(self, obj_id, key):
        """
        Check if the attribute exists.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        records = self.model.objects.filter(obj_id=obj_id, key=key)
        return len(records) != 0

    def get(self, obj_id, key, **kwargs):
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
        records = self.model.objects.filter(obj_id=obj_id, key=key)
        if len(records) == 0:
            try:
                return kwargs["default"]
            except KeyError:
                raise AttributeError

        return from_string(records[0].value)

    def get_obj(self, obj_id):
        """
        Get values of an object.

        Args:
            obj_id: (number) object's id.
        """
        records = self.model.objects.filter(obj_id=obj_id)
        return dict((r.key, from_string(r.value)) for r in records)

    def remove(self, obj_id, key):
        """
        Remove an attribute of an object.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        self.model.objects.filter(obj_id=obj_id, key=key).delete()

    def remove_obj(self, obj_id):
        """
        Remove an object's all attributes.

        Args:
            obj_id: (number) object's id.
        """
        self.model.objects.filter(obj_id=obj_id).delete()
