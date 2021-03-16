"""
The base class of key value storage.
"""


class BaseKeyValueStorage(object):
    """
    The storage of key-values.
    """
    def __init__(self, model_name):
        # db model
        self.model_name = model_name

    def add(self, category, key, value):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    def add_dict(self, category, key, value_dict):
        """
        Add a new dict to the key. If the key already exists, raise an exception.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value_dict: (dict) attribute's value.
        """
        pass

    def save(self, category, key, value):
        """
        Set an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    def save_dict(self, category, key, value_dict):
        """
        Save a dict to the key.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value_dict: (dict) attribute's value.
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

    def load(self, category, key, *default):
        """
        Get the value of an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            default: (any or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        pass

    def load_dict(self, category, key, **default):
        """
        Get a dict of values of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (dict or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        pass

    def load_category_dict(self, category):
        """
        Get all dicts of a category.

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
