"""
Key value storage in relational database with write back memory cache.
"""

from django.apps import apps
from django.conf import settings
from django.db import IntegrityError
from django.db.transaction import atomic
from muddery.server.database.storage.kv_table import KeyValueTable
from muddery.server.utils.exception import MudderyError, ERR


class KeyValueWriteBackTable(KeyValueTable):
    """
    The storage of object attributes.
    """
    def __init__(self, model_name, category_field, key_field, default_value_field=None):
        super(KeyValueWriteBackTable, self).__init__(model_name, category_field, key_field, default_value_field)

        # memory cache
        self.cache = {}

    def add_dict(self, category, key, value_dict):
        """
        Set a set of values.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value_dict: (dict) data.
        """
        self.check_category_cache(category)
        if key in self.cache[category]:
            raise IntegrityError("Duplicate key %s." % key)
        self.cache[category][key] = value_dict

        super(KeyValueWriteBackTable, self).add_dict(category, key, value_dict)

    def save_dict(self, category, key, value_dict):
        """
        Set a set of values.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value_dict: (dict) data.
        """
        self.check_category_cache(category)
        if key in self.cache[category]:
            self.cache[category][key].update(value_dict)
        else:
            self.cache[category][key] = value_dict
        super(KeyValueWriteBackTable, self).save_dict(category, key, value_dict)

    def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        self.check_category_cache(category)
        return key in self.cache[category]

    def load(self, category, key, *default):
        """
        Get the value of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (any or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        self.check_category_cache(category)
        try:
            return self.cache[category][key][self.default_value_field]
        except KeyError:
            if len(default) > 0:
                return default[0]
            else:
                raise AttributeError

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
        self.check_category_cache(category)
        try:
            return self.cache[category][key].copy()
        except KeyError:
            if default is not None:
                return default
            else:
                raise AttributeError

    def load_category(self, category):
        """
        Get all default field's values of a category.

        Args:
            category: (string) category's name.
        """
        self.check_category_cache(category)
        return {
            key: values[self.default_value_field] for key, values in self.cache[category].items()
        }

    def load_category_dict(self, category):
        """
        Get all dicts of a category.

        Args:
            category: (string) category's name.
        """
        self.check_category_cache(category)
        return self.cache[category].copy()

    def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.

        Return:
            (dict): deleted values
        """
        try:
            del self.cache[category][key]
        finally:
            return super(KeyValueWriteBackTable, self).delete(category, key)

    def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.

        Return:
            (dict): deleted values
        """
        try:
            del self.cache[category]
        finally:
            return super(KeyValueWriteBackTable, self).delete_category(category)

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        return atomic()

    def check_category_cache(self, category):
        """
        Load a category's data from db if have not loaded this category.
        :param category:
        :return:
        """
        if category not in self.cache:
            self.cache[category] = super(KeyValueWriteBackTable, self).load_category_dict(category)
