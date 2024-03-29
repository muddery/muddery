"""
Attributes are arbitrary data stored on objects. Attributes supports
both pure-string values and pickled arbitrary data.

Attributes are also used to implement Nicks. This module also contains
the Attribute- and NickHandlers as well as the `NAttributeHandler`,
which is a non-db version of Attributes.

"""

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
    def __init__(self, obj_id, storage_class):
        """Initialize handler."""
        self.obj_id = obj_id
        self.storage = storage_class()

    async def has(self, key):
        """
        Checks if the given Attribute exists on the object.

        Args:
            key (str): The Attribute key to check for.

        Returns:
            has_attribute (bool): If the Attribute exists on this object or not.
        """
        return await self.storage.has(self.obj_id, key=key)

    async def load(self, key, default=None):
        """
        Get the Attribute.

        Args:
            key (str): the attribute identifier.
            default (any or none): default value.

        Returns:
            result (any): The value matches the key.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.

        """
        return await self.storage.load(self.obj_id, key, default)

    async def save(self, key, value):
        """
        Add attribute to object.

        Args:
            key (str): An Attribute name to add.
            value (any or str): The value of the Attribute. If
                `strattr` keyword is set, this *must* be a string.
        """
        await self.storage.save(self.obj_id, key, value)

    async def saves(self, value_dict):
        """
        Set attributes.
        """
        await self.storage.save_keys(self.obj_id, value_dict)

    async def delete(self, key):
        """
        Remove an attribute from object.

        Args:
            key (str ): An Attribute key to remove keys.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key`.

        Notes:
            If neither key nor category is given, this acts as clear().

        """
        await self.storage.delete(self.obj_id, key)

    async def clear(self):
        """
        Remove all Attributes on this object.
        """
        await self.storage.remove_obj(self.obj_id)

    async def all(self):
        """
        Get all attributes from an object.
        """
        return await self.storage.load_obj(self.obj_id)

    def transaction(self):
        """
        Begin a transaction.
        """
        return self.storage.transaction()
