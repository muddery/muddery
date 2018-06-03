"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class NPCDialoguesMapper(object):
    """
    NPC's dialogue list.
    """
    def __init__(self):
        self.model_name = "npc_dialogues"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def filter(self, npc):
        """
        Get NPC's dialogues.

        Args:
            npc: (string) NPC's key.
        """
        return self.objects.filter(npc=npc)


NPC_DIALOGUES = NPCDialoguesMapper()

