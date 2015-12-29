"""
Data are arbitrary data stored in worlddata tables. They are read only.

"""
from builtins import object
import weakref


class DataFieldHandler(object):
    """
    This handler manages read only data from db.
    It is similar to `NAttributeHandler` and is used
    by the `.data` handler in the same way as `.ndb` does
    for the `NAttributeHandler`.
    """
    def __init__(self, obj):
        """
        Initialized on the object
        """
        self._store = {}
        self.obj = weakref.proxy(obj)

    def has(self, key):
        """
        Check if object has this data or not.

        Args:
            key (str): The Data key to check.

        Returns:
            has_data (bool): If Data is set or not.

        """
        return key in self._store

    def get(self, key):
        """
        Get the named key value.

        Args:
            key (str): The Data key to get.

        Returns:
            the value of the Data.
        """
        if key not in self._store:
            raise AttributeError
        return self._store.get(key)

    def add(self, key, value):
        """
        Add new key and value.

        Args:
            key (str): The name of Nattribute to add.
            value (any): The value to store.

        """
        self._store[key] = value

    def clear(self):
        """
        Remove all NAttributes from handler.

        """
        self._store = {}

    def all(self, return_tuples=False):
        """
        List the contents of the handler.

        Args:
            return_tuples (bool, optional): Defines if the Data
                are returns as a list of keys or as a list of `(key, value)`.

        Returns:
            data (list): A list of keys `[key, key, ...]` or a
                list of tuples `[(key, value), ...]` depending on the
                setting of `return_tuples`.

        """
        if return_tuples:
            return [(key, value) for (key, value) in self._store.items()]
        return [key for key in self._store]
