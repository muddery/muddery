"""
Attributes are arbitrary data stored on objects. Attributes supports
both pure-string values and pickled arbitrary data.

Attributes are also used to implement Nicks. This module also contains
the Attribute- and NickHandlers as well as the `NAttributeHandler`,
which is a non-db version of Attributes.

"""

import weakref

from django.apps import apps
from django.conf import settings
from muddery.server.database.storage.memory_cache import MemoryCache
from muddery.server.database.storage.atomic import Atomic

# -------------------------------------------------------------
#
#   Attributes
#
# -------------------------------------------------------------


#
# Handlers making use of the Attribute model
#
class ObjectStatesHandler(object):
    """
    Handler for adding Attributes to the object.
    """
    def __init__(self, obj):
        """Initialize handler."""
        self.obj = weakref.proxy(obj)
        self.obj_id = obj.id

        self.cache = MemoryCache("object_status")

    def has(self, key):
        """
        Checks if the given Attribute exists on the object.

        Args:
            key (str): The Attribute key to check for.

        Returns:
            has_attribute (bool): If the Attribute exists on this object or not.
        """
        return self.cache.has(self.obj_id, key=key)

    def load(self, key, default=None):
        """
        Get the Attribute.

        Args:
            key (str): the attribute identifier.
            default (any or none): default value.

        Returns:
            result (any): The value matches the key.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.

        """
        return self.cache.load(self.obj_id, key, default)

    def save(self, key, value):
        """
        Add attribute to object.

        Args:
            key (str): An Attribute name to add.
            value (any or str): The value of the Attribute. If
                `strattr` keyword is set, this *must* be a string.
        """
        self.cache.save(self.obj_id, key, value)

    def saves(self, value_dict):
        """
        Set attributes.
        """
        self.cache.saves(self.obj_id, value_dict)

    def delete(self, key):
        """
        Remove an attribute from object.

        Args:
            key (str ): An Attribute key to remove keys.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key`.

        Notes:
            If neither key nor category is given, this acts as clear().

        """
        self.cache.delete(self.obj_id, key)

    def clear(self):
        """
        Remove all Attributes on this object.
        """
        self.cache.remove_obj(self.obj_id)

    def all(self):
        """
        Get all attributes from an object.
        """
        return self.cache.load_obj(self.obj_id)

    def atomic(self):
        """
        Begin a transaction.
        """
        return Atomic(self.cache)
