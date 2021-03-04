"""
Object's attributes cache.
"""


class BaseKeyValueStorage(object):
    """
    The storage of key-values.
    """
    def __init__(self, model_name):
        # db model
        self.model_name = model_name

    def save(self, category, key, value):
        """
        Set an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    def saves(self, category, value_dict):
        """
        Set attributes.

        Args:
            category: (string, int) the category of data.
            value_dict: (dict) a dict of key-values.
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

    def load(self, category, key, *args):
        """
        Get the value of an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            args: (any or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
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

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        pass
