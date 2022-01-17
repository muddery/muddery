"""
The base class of key value storage.
"""
from muddery.server.database.storage.base_transaction import BaseTransaction


class BaseKeyValueStorage(object):
    """
    The storage of key-values.
    """
    def __init__(self):
        self.trans = BaseTransaction()

    async def add(self, category, key, value=None):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    async def save(self, category, key, value=None):
        """
        Set an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    async def has(self, category, key):
        """
        Check if the attribute exists.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
        """
        pass

    async def all(self):
        """
        Get all data.
        :return:
        """
        pass

    async def load(self, category, key, *default):
        """
        Get the value of an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        pass

    async def load_category(self, category):
        """
        Get all a category's data.

        Args:
            category: (string) category's name.
        """
        pass

    async def delete(self, category, key):
        """
        delete an attribute of an object.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
        """
        pass

    async def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        pass

    def transaction(self):
        """
        Guarantee the transaction execution of a given block.
        """
        return self.trans
