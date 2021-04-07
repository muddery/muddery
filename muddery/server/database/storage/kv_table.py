"""
Key value storage in relational database.
"""

from django.apps import apps
from django.conf import settings
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import atomic
from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage
from muddery.server.utils.exception import MudderyError, ERR


class KeyValueTable(BaseKeyValueStorage):
    """
    The storage of object attributes.
    """
    def __init__(self, model_name, category_field, key_field, default_value_field=None):
        """

        :param model_name: table's model
        :param category_field: category's field name in the table
        :param key_field: key's field name in the table
        :param default_value_field: default value's field name in the table
        """
        super(KeyValueTable, self).__init__(model_name)

        # db model
        self.model = apps.get_model(settings.GAME_DATA_APP, self.model_name)
        self.fields = [field.name for field in self.model._meta.fields]
        self.category_field = category_field
        self.key_field = key_field
        self.default_value_field = default_value_field

    def add(self, category, key, value):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        self.add_dict(category, key, {self.default_value_field: value})

    def add_dict(self, category, key, value_dict):
        """
        Add a new dict to the key. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value_dict: (dict) data.
        """
        data = {
            self.key_field: key,
        }
        data.update(value_dict)
        if self.category_field:
            data[self.category_field] = category

        self.model.objects.create(**data)

    def save(self, category, key, value):
        """
        Set a value to the default value field.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        self.save_dict(category, key, {self.default_value_field: value})

    def save_dict(self, category, key, value_dict):
        """
        Set a set of values.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value_dict: (dict) data.
        """
        data = {
            self.key_field: key,
            "defaults": value_dict
        }
        if self.category_field:
            data[self.category_field] = category

        self.model.objects.update_or_create(**data)

    def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        query = {
            self.key_field: key,
        }
        if self.category_field:
            query[self.category_field] = category

        return self.model.objects.filter(**{
            self.category_field: category,
            self.key_field: key,
        }).count() > 0

    def load(self, category, key, *default):
        """
        Get the default field value of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (any or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        query = {
            self.key_field: key,
        }
        if self.category_field:
            query[self.category_field] = category

        try:
            record = self.model.objects.get(**query)
        except ObjectDoesNotExist:
            if len(default) > 0:
                return default[0]
            else:
                raise AttributeError

        return record.serializable_value(self.default_value_field)

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
        query = {
            self.key_field: key,
        }
        if self.category_field:
            query[self.category_field] = category

        try:
            record = self.model.objects.get(**query)
        except ObjectDoesNotExist:
            if default is not None:
                return default
            else:
                raise AttributeError

        return {name: record.serializable_value(name) for name in self.fields}

    def load_category(self, category):
        """
        Get all default field's values of a category.

        Args:
            category: (string) category's name.
        """
        if self.category_field:
            records = self.model.objects.filter(**{
                self.category_field: category,
            })
        else:
            records = self.model.objects.all()

        return {
            r.serializable_value(self.key_field): r.serializable_value(self.default_value_field) for r in records
        }

    def load_category_dict(self, category):
        """
        Get all dicts of a category.

        Args:
            category: (string) category's name.
        """
        if self.category_field:
            records = self.model.objects.filter(**{
                self.category_field: category,
            })
        else:
            records = self.model.objects.all()

        return {
            r.serializable_value(self.key_field): {
                name: r.serializable_value(name) for name in self.fields
            } for r in records
        }

    def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        query = {
            self.key_field: key,
        }
        if self.category_field:
            query[self.category_field] = category

        self.model.objects.filter(**query).delete()

    def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        if self.category_field:
            self.model.objects.filter(**{
                self.category_field: category,
            }).delete()
        else:
            self.model.objects.all().delete()

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        return atomic()
