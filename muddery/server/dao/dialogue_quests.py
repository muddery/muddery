"""
Query and deal common tables.
"""

from muddery.server.dao.base_query import BaseQuery
from muddery.server.dao.worlddata import WorldData


class DialogueQuests(BaseQuery):
    """
    All dialogues and quests relations.
    """
    table_name = "dialogue_quest_dependencies"

    @classmethod
    def get(cls, dialogue_key):
        """
        Get a dialogue by its key.
        """
        return WorldData.get_table_data(cls.table_name, dialogue=dialogue_key)
