"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class QuestDependencies(BaseQuery):
    """
    All quest conditions.
    """
    table_name = "quest_dependencies"

    @classmethod
    def get(cls, quest_key):
        """
        Get a quest dependencies by quest's key.
        """
        return WorldData.get_table_data(cls.table_name, quest=quest_key)
