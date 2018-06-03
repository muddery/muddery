"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class DefaultObjectsMapper(object):
    """
    Character's default objects.
    """
    def __init__(self):
        self.model_name = "default_objects"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def filter(self, character):
        """
        Get character's default objects.

        Args:
            character: (string) character's key.
        """
        return self.objects.filter(character=character)


DEFAULT_OBJECTS = DefaultObjectsMapper()

