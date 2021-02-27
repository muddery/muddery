"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class QuestObjectives(BaseQuery):
    """
    Quest's objectives.
    """
    table_name = "quest_objectives"

    @classmethod
    def get(cls, quest):
        """
        Get properties by element's name.
        """
        return WorldData.get_table_data(cls.table_name, quest=quest)
