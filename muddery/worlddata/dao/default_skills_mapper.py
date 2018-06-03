"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class DefaultSkillsMapper(object):
    """
    Character's default skills.
    """
    def __init__(self):
        self.model_name = "default_skills"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def filter(self, character):
        """
        Get character's default skills.

        Args:
            character: (string) character's key.
        """
        return self.objects.filter(character=character)


DEFAULT_SKILLS = DefaultSkillsMapper()

