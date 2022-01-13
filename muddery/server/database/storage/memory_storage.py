"""
Key value storage in relational database.
"""

from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage
from muddery.server.utils.exception import MudderyError, ERR


class MemoryStorage(BaseKeyValueStorage):
    """
    The storage of object attributes.
    """
    def __init__(self):
        """

        """
        super(MemoryStorage, self).__init__()
        self.storage = {}

    async def add(self, category, key, value=None):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        if category not in self.storage:
            self.storage[category] = {}

        if key in self.storage[category]:
            raise MudderyError(ERR.duplicate_key, "Duplicate key %s." % key)

        self.storage[category][key] = value

    async def save(self, category, key, value=None):
        """
        Set a value to the default value field.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        if category not in self.storage:
            self.storage[category] = {}

        if key in self.storage[category] and type(self.storage[category][key]) == dict:
            self.storage[category][key].update(value)
        else:
            self.storage[category][key] = value

    async def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        return category in self.storage and key in self.storage[category]

    async def all(self):
        """
        Get all data.
        :return:
        """
        return self.storage.copy()

    async def load(self, category, key, *default):
        """
        Get the default field value of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        try:
            return self.storage[category][key]
        except KeyError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e

    async def load_category(self, category):
        """
        Get all default field's values of a category.

        Args:
            category: (string) category's name.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `category`.
        """
        if category not in self.storage:
            raise KeyError

        return self.storage[category].copy()

    async def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        try:
            del self.storage[category][key]
        except KeyError:
            pass

    async def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        try:
            del self.storage[category]
        except KeyError:
            pass
