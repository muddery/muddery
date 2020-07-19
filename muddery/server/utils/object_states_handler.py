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

from muddery.server.database.attributes_cache.base_cache import BaseAttributesCache


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
        self.states = obj.states

        if self.states:
            self.obj_id = obj.id

            apps.get_model(settings.GAME_DATA_APP, obj.model_name)
            self.model_name = obj.model_name

            self.cache = BaseAttributesCache(self.model_name)

    def has(self, key):
        """
        Checks if the given Attribute exists on the object.

        Args:
            key (str): The Attribute key to check for.

        Returns:
            has_attribute (bool): If the Attribute exists on this object or not.
        """
        if key not in self.states:
            return super(type(self.obj), self.obj).state.has(key)

        return self.cache.has(self.obj_id, key=key)

    def get(self, key):
        """
        Get the Attribute.

        Args:
            key (str): the attribute identifier.

        Returns:
            result (any): The value matches the key.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key`.

        """
        if key not in self.states:
            return super(type(self.obj), self.obj).state.get(key)

        return self.cache.get(self.obj_id, key)

    def add(self, key, value):
        """
        Add attribute to object.

        Args:
            key (str): An Attribute name to add.
            value (any or str): The value of the Attribute. If
                `strattr` keyword is set, this *must* be a string.
        """
        if key not in self.states:
            return super(type(self.obj), self.obj).state.add(key, value)

        self.cache.set(self.obj_id, key, value)

    def remove(self, key):
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
        if key not in self.states:
            return super(type(self.obj), self.obj).state.remove(key)

        self.cache.remove(self.obj_id, key)

    def clear(self):
        """
        Remove all Attributes on this object.
        """
        self._clear(self.obj_id)

    def _clear(self, obj_id):
        """
        Remove all Attributes on this object recursively.

        Args:
            obj_id (number): object's record id.
        """
        super(type(self.obj), self.obj).state._clear(obj_id)
        self.cache.remove_obj(self.obj_id)

    def all(self):
        """
        Get all attributes from an object.
        """
        return self.cache.get_obj(self.obj_id)

    def _all(self, obj_id):
        """
        Get all attributes from an object recursively.

        Args:
            obj_id (number): object's record id.

        Return:
            (dict): object's attributes.
        """
        attributes = super(type(self.obj), self.obj).state._all(obj_id)
        attributes.update(self.cache.get_obj(self.obj_id))

        return attributes
