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
        self.all_cached = False

    def add(self, category, key, value):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        self.check_category_cache(category)
        if category not in self.cache:
            self.cache[category] = {}

        if key in self.cache[category]:
            raise IntegrityError("Duplicate key %s." % key)

        self.cache[category][key] = value

        super(KeyValueWriteBackTable, self).add(category, key, value)

    def save(self, category, key, value):
        """
        Set a value to the default value field.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        self.check_category_cache(category)
        if category not in self.cache:
            self.cache[category] = {}

        if key in self.cache[category] and type(self.cache[category][key]) == dict:
            self.cache[category][key].update(value)
        else:
            self.cache[category][key] = value

        super(KeyValueWriteBackTable, self).save(category, key, value)

    def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        self.check_category_cache(category)
        return category in self.cache and key in self.cache[category]

    def all(self):
        """
        Get all data.
        :return:
        """
        self.check_all_cache()
        return self.cache.copy()

    def load(self, category, key, *default):
        """
        Get the value of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        self.check_category_cache(category)
        try:
            return self.cache[category][key]
        except KeyError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e

    def load_category(self, category, *default):
        """
        Get all default field's values of a category.

        Args:
            category: (string) category's name.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `category`.
        """
        self.check_category_cache(category)
        if category not in self.cache:
            if len(default) > 0:
                return default[0]
            else:
                raise KeyError

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
        except KeyError:
            pass

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
        except KeyError:
            pass

        return super(KeyValueWriteBackTable, self).delete_category(category)

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        return atomic()

    def check_all_cache(self):
        """
        Load all data from db if have not loaded this category.
        :param category:
        :return:
        """
        if not self.all_cached:
            all_data = super(KeyValueWriteBackTable, self).all()
            self.cache = {category: data for category, data in all_data.items()}
            self.all_cached = True

    def check_category_cache(self, category):
        """
        Load a category's data from db if have not loaded this category.
        :param category:
        :return:
        """
        if category not in self.cache:
            try:
                data = super(KeyValueWriteBackTable, self).load_category(category)
                self.cache[category] = data
            except KeyError:
                pass
