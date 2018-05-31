"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class DialogueQuestDependenciesMapper(object):
    """
    Dialogue question's relation.
    """
    def __init__(self):
        self.model_name = "dialogue_quest_dependencies"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get(self, key):
        """
        Get dialogue question's relation.

        Args:
            key: (string) dialogue's key.
        """
        return self.objects.filter(dialogue=key)


DIALOGUE_QUESTION_RELATIONS = DialogueQuestDependenciesMapper()

