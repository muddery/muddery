"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

import os
from django.conf import settings
from evennia.utils import search, logger


def get_muddery_version():
    """
    Get muddery's version.
    """
    import muddery
    return muddery.__version__


def set_obj_data_key(obj, key):
    """
    Set data key. Put it info into an object's attributes.
            
    Args:
        obj: (object) object to be set
        key: (string) key of the data.
    """
    obj.attributes.add("key", key, category=settings.DATA_KEY_CATEGORY, strattr=True)


def search_obj_data_key(key):
    """
    Search objects which have the given key.

    Args:
        key: (string) Data's key.
    """
    if not key:
        return None

    obj = search.search_object_attribute(key="key", strvalue=key, category=settings.DATA_KEY_CATEGORY)
    return obj


def set_obj_unique_type(obj, type):
    """
    Set unique object's type.

    Args:
        obj: (object) object to be set
        type: (string) unique object's type.
    """
    obj.attributes.add("type", type, category=settings.DATA_KEY_CATEGORY, strattr=True)


def search_obj_unique_type(type):
    """
    Search objects which have the given unique type.

    Args:
        type: (string) unique object's type.
    """
    obj = search.search_object_attribute(key="type", strvalue=type, category=settings.DATA_KEY_CATEGORY)
    return obj
