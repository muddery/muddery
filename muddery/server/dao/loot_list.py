"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class BaseLootList(object):
    """
    Equipment positions data.
    """
    table_name = ""

    @classmethod
    def get(cls, provider_key):
        """
        Get a loot list by its key.
        """
        return WorldData.get_table_data(cls.table_name, "provider", provider_key)


class CharacterLootList(BaseLootList):
    """
    Character's loot list.
    """
    table_name = "character_loot_list"


class CreatorLootList(BaseLootList):
    """
    Object creator's loot list.
    """
    table_name = "creator_loot_list"


class QuestLootList(BaseLootList):
    """
    Object creator's loot list.
    """
    table_name = "quest_reward_list"
