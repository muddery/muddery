"""
Query and deal common tables.
"""

from muddery.server.dao.base_query import BaseQuery
from muddery.server.dao.worlddata import WorldData


class Dialogues(BaseQuery):
    """
    All dialogues.
    """
    table_name = "dialogues"

    @classmethod
    def get(cls, dialogue_key):
        """
        Get a dialogue by its key.
        """
        return WorldData.get_table_data(cls.table_name, key=dialogue_key)
