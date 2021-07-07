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
        :param default_value_field: default value's field name in the table.
                If set the default value field, it can only store a simple value.
                If the default value field is not set, value should be a dict.
        """
        super(KeyValueTable, self).__init__()

        # db model
        self.model_name = model_name
        self.model = apps.get_model(settings.GAME_DATA_APP, self.model_name)

        exclude_fields = set()
        self.category_field = category_field
        if category_field:
            exclude_fields.add(category_field)

        self.key_field = key_field
        if key_field:
            exclude_fields.add(key_field)

        self.default_value_field = default_value_field
        if default_value_field:
            exclude_fields.add(default_value_field)

        self.fields = [field.name for field in self.model._meta.fields if field.name not in exclude_fields]

    def add(self, category, key, value=None):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        if value is None:
            data = {}
        elif self.default_value_field is None:
            data = value
        else:
            data = {self.default_value_field: value}

        if self.category_field:
            data[self.category_field] = category

        if self.key_field:
            data[self.key_field] = key

        self.model.objects.create(**data)

    def save(self, category, key, value=None):
        """
        Set a value to the default value field.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        if value is None:
            data = {}
        elif self.default_value_field is None:
            data = value
        else:
            data = {self.default_value_field: value}

        params = {
            "defaults": data
        }

        if self.category_field:
            params[self.category_field] = category

        if self.key_field:
            params[self.key_field] = key

        self.model.objects.update_or_create(**params)

    def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        query = {}

        if self.category_field:
            query[self.category_field] = category

        if self.key_field:
            query[self.key_field] = key

        return self.model.objects.filter(**query).count() > 0

    def all(self):
        """
        Get all data.
        :return:
        """
        records = self.model.objects.all()

        all_data = {}
        if self.category_field:
            for r in records:
                category = r.serializable_value(self.category_field)
                if category not in all_data:
                    all_data[category] = {}

                key = r.serializable_value(self.key_field) if self.key_field else ""
                all_data[category][key] = {name: r.serializable_value(name) for name in self.fields}
        elif self.key_field:
            all_data[""] = {
                r.serializable_value(self.key_field): {
                    name: r.serializable_value(name) for name in self.fields
                } for r in records
            }
        elif len(records) > 0:
            all_data[""][""] = {
                name: records[0].serializable_value(name) for name in self.fields
            }
        else:
            all_data[""][""] = {}

        if self.default_value_field is not None:
            all_data = {key: value[self.default_value_field] for category, data in all_data.items() for key, value in data.items()}

        return all_data

    def load(self, category, key, *default):
        """
        Get the default field value of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        query = {}

        if self.category_field:
            query[self.category_field] = category

        if self.key_field:
            query[self.key_field] = key

        try:
            record = self.model.objects.get(**query)
        except ObjectDoesNotExist:
            if len(default) > 0:
                return default[0]
            else:
                raise KeyError

        if self.default_value_field is not None:
            return record.serializable_value(self.default_value_field)
        else:
            return {name: record.serializable_value(name) for name in self.fields}

    def load_category(self, category, *default):
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

        if len(records) == 0:
            if len(default) > 0:
                return default[0]
            else:
                raise KeyError

        if self.key_field:
            data = {
                record.serializable_value(self.key_field): record for record in records
            }
        else:
            data = {
                "": record for record in records
            }

        if self.default_value_field is not None:
            data = {key: record.serializable_value(self.default_value_field) for key, record in data.items()}
        else:
            data = {key: {name: record.serializable_value(name) for name in self.fields} for key, record in data.items()}

        return data

    def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        query = {}

        if self.category_field:
            query[self.category_field] = category

        if self.key_field:
            query[self.key_field] = key

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
