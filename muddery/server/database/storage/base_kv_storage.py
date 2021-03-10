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

    def save(self, category, key, value):
        """
        Set an attribute.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value: (string) attribute's value.
        """
        pass

    def save_keys(self, category, values_dict):
        """
        Set attributes to multiple keys.

        Args:
            category: (string, int) the category of data.
            values_dict: (dict) a dict of key-values.
        """
        with self.atomic():
            for key, value in values_dict.items():
                self.save(category, key, value)

    def save_dict(self, category, key, value_dict):
        """
        Save a dict to the key.

        Args:
            category: (string, int) the category of data.
            key: (string) attribute's key.
            value_dict: (dict) attribute's value.
        """
        pass

    def save_keys_dict(self, category, values_dict):
        """
        Save dicts to multiple keys.

        Args:
            category: (string, int) the category of data.
            values_dict: (dict) a dict of key-values.
        """
        with self.atomic():
            for key, value in values_dict.items():
                self.save_dict(category, key, value)

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

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        pass
