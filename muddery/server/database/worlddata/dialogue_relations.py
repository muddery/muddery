"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.worlddata import WorldData


class DialogueRelations(object):
    """
    All dialogue relations.
    """
    table_name = "dialogue_relations"

    @classmethod
    def get(cls, dialogue_key):
        """
        Get a dialogue by its key.
        """
        return WorldData.get_table_data(cls.table_name, dialogue=dialogue_key)
