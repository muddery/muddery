"""
Query and deal common tables.
"""

from muddery.server.dao.base_query import BaseQuery
from muddery.server.dao.worlddata import WorldData


class DialogueSentences(BaseQuery):
    """
    All sentences in dialogues.
    """
    table_name = "dialogue_sentences"

    @classmethod
    def get(cls, dialogue_key):
        """
        Get a dialogue by its key.
        """
        return WorldData.get_table_data(cls.table_name, dialogue=dialogue_key)
