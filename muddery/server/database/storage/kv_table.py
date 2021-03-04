"""
Object's attributes cache.
"""

from django.apps import apps
from django.conf import settings
from django.db.transaction import atomic
from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage
from muddery.server.utils.exception import MudderyError, ERR


class KeyValueTable(BaseKeyValueStorage):
    """
    The storage of object attributes.
    """
    def __init__(self, model_name, category_column=None):
        super(KeyValueTable, self).__init__(model_name)

        # db model
        self.model = apps.get_model(settings.GAME_DATA_APP, self.model_name)
        self.category_column = "category" if category_column is None else category_column

    def save(self, category, key, value):
        """
        Set a value.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        self.model.objects.update_or_create(**{
            self.category_column: category,
            "key": key,
            "defaults": {
                "value": value,
            }
        })

    def saves(self, category, value_dict):
        """
        Set values.

        Args:
            category: (string) the category of data.
            value_dict: (dict) a dict of key-values.
        """
        for key, value in value_dict.items():
            self.save(category, key, value)

    def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        return self.model.objects.filter(**{
            self.category_column: category,
            "key": key,
        }).count() > 0

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
        try:
            record = self.model.objects.get(**{
                self.category_column: category,
                "key": key,
            })
            return record.value
        except:
            if len(default) > 0:
                return default[0]
            else:
                raise AttributeError

    def load_category(self, category):
        """
        Get all values of a category.

        Args:
            category: (string) category's name.
        """
        records = self.model.objects.filter(**{
            self.category_column: category,
        })
        return {
            r.key: r.value for r in records
        }

    def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.

        Return:
            (list): deleted values
        """
        records = self.model.objects.filter(**{
            self.category_column: category,
            "key": key,
        })
        values = [r.value for r in records]
        records.delete()
        return values

    def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.

        Return:
            (list): deleted values
        """
        records = self.model.objects.filter(**{
            self.category_column: category,
        })
        values = [r.value for r in records]
        records.delete()
        return values

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        return atomic()
