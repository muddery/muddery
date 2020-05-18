"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class Dialogues(object):
    """
    All dialogues.
    """
    table_name = "dialogues"

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
        return WorldData.get_table_data(cls.table_name, "key", dialogue_key)
