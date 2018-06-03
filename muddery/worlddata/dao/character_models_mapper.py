"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class CharacterModelsMapper(object):
    """
    Character models mapper.
    """
    def __init__(self):
        self.model_name = "character_models"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get_data(self, key, level=1):
        """
        Get model's data.

        Args:
            key: (string) models's key.
            level: (integer) character's leve.
        """
        record = self.objects.get(key=key, level=level)

        reserved_fields = {"id", "key", "name", "level"}
        data = {}
        for field in record._meta.fields:
            if field.name in reserved_fields:
                continue
            data[field.name] = record.serializable_value(field.name)

        return data


CHARACTER_MODELS = CharacterModelsMapper()

