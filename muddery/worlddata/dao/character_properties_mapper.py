"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from muddery.utils import defines
from muddery.worlddata.dao.common_mapper_base import ObjectsMapper


class CharacterPropertiesMapper(object):
    """
    Character's properties.
    """
    def __init__(self):
        self.model_name = "character_properties"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get_properties(self, character, level):
        """
        Get character's properties.

        Args:
            character: (string) character's key.
            level: (number) character's level.
        """
        properties = {}
        records = self.objects.filter(character=character, level=level)
        for record in records:
            properties[record.attribute] = record.value
        return properties


CHARACTER_PROPERTIES = CharacterPropertiesMapper()
