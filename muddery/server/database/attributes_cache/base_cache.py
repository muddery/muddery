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
        raise MudderyError(ERR.server_error, "The object could not be stored.")

    return str_value


def from_string(str_value):
    # unpack a value from a string.
    try:
        json_value, data_type = json.dumps(str_value)
        if data_type in ("str", "int", "float", "bool", "bytes"):
            value = eval(data_type)(json_value)
        elif data_type in ("ObjectDB", "ScriptDB", "AccountDB", "ChannelDB"):
            model = eval(data_type)
            value = model.objects.get(id=json_value)
        elif data_type in ("dict", "OrderedDict"):
            value = eval(data_type)((from_string(key), from_string(item) for key, item in json_value))
        else:
            value = eval(data_type)(from_string(item) for item in json_value)
    except Exception as e:
        raise MudderyError(ERR.server_error, "The object could not be loaded.")

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
        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            value: (any) attribute's value.
        """
        str_value = to_string(value)
        record = {
            obj_id: obj_id,
            key: key,
            value: str_value,
        }
        data = self.model(**record)
        data.full_clean()
        data.save()

    def get(self, obj_id, key):
        records = self.model.objects.filter(obj_id=obj_id, key=key)
        if len(records) == 0:
            return None

        return from_string(records[0].value)
