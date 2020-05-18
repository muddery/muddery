"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class DialogueRelations(object):
    """
    All dialogue relations.
    """
    table_name = "dialogue_relations"

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)

    @classmethod
    def get(cls, dialogue_key):
        """
        Get a dialogue by its key.
        """
        return WorldData.get_table_data(cls.table_name, "dialogue", dialogue_key)
