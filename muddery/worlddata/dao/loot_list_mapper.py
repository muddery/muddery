"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class LootListMapper(object):
    """
    General loot list mapper.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def filter(self, object_key):
        """
        Get object's loot list.
        """
        return self.objects.filter(provider=object_key)


CHARACTER_LOOT_LIST = LootListMapper("character_loot_list")

CREATOR_LOOT_LIST = LootListMapper("creator_loot_list")

QUEST_REWARD_LIST = LootListMapper("quest_reward_list")

