"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class QuestObjectives(object):
    """
    Quest's objectives.
    """
    table_name = "quest_objectives"

    @classmethod
    def get(cls, quest):
        """
        Get properties by typeclass's name.
        """
        return WorldData.get_table_data(cls.table_name, quest=quest)
