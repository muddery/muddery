"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class DialogueSentencesMapper(object):
    """
    NPC's dialogue sentences.
    """
    def __init__(self):
        self.model_name = "dialogue_sentences"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def filter(self, key):
        """
        Get dialogue sentences.

        Args:
            key: (string) dialogue's key.
        """
        return self.objects.filter(dialogue=key)


DIALOGUE_SENTENCES = DialogueSentencesMapper()

