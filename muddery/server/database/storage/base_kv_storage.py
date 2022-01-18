"""
The base class of key value storage.
"""

from asyncio import Lock


class BaseKeyValueStorage(object):
    """
    The storage of key-values.
    """
    def __init__(self):
        self.lock = Lock()

    async def add(self, category: str, key: str, value: any = None) -> None:
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    async def save(self, category: str, key: str, value: any = None) -> None:
        """
        Set an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    async def has(self, category: str, key: str) -> bool:
        """
        Check if the attribute exists.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
        """
        pass

    async def all(self) -> dict:
        """
        Get all data.
        :return:
        """
        pass

    async def load(self, category: str, key: str, *default, for_update=False) -> any:
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

    async def load_category(self, category: str, *default) -> any:
        """
        Get all a category's data.

        Args:
            category: (string) category's name.
        """
        pass

    async def delete(self, category: str, key: str) -> any:
        """
        delete an attribute of an object.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
        """
        pass

    async def delete_category(self, category: str) -> dict:
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        pass

    def transaction(self) -> any:
        """
        Guarantee the transaction execution of a given block.
        """
        pass
