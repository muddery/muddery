"""
The base class of key value storage.
"""


class BaseKeyValueStorage(object):
    """
    The storage of key-values.
    """
    def add(self, category, key, value=None):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    def save(self, category, key, value=None):
        """
        Set an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    def has(self, category, key):
        """
        Check if the attribute exists.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
        """
        pass

    def all(self):
        """
        Get all data.
        :return:
        """
        pass

    def load(self, category, key, *default):
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

    def load_category(self, category):
        """
        Get all a category's data.

        Args:
            category: (string) category's name.
        """
        pass

    def delete(self, category, key):
        """
        delete an attribute of an object.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
        """
        pass

    def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        pass

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        pass
