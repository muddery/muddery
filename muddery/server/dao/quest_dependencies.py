"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class QuestDependencies(object):
    """
    All quest conditions.
    """
    table_name = "quest_dependencies"

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)

    @classmethod
    def get(cls, quest_key):
        """
        Get a dialogue by its key.
        """
        return WorldData.get_table_data(cls.table_name, quest=quest_key)
