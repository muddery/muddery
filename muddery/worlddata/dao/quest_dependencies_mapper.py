"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class QuestDependenciesMapper(object):
    """
    Quest's dependencies.
    """
    def __init__(self):
        self.model_name = "quest_dependencies"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get(self, quest):
        """
        Get quest's dependencies.

        Args:
            quest: (string) qeust's key.
        """
        return self.objects.filter(quest=quest)


QUEST_DEPENDENCIES = QuestDependenciesMapper()

