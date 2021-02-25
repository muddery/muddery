"""
Query and deal common tables.
"""

from muddery.server.database.dao.base_query import BaseQuery
from muddery.server.database.dao.worlddata import WorldData


class DefaultObjects(BaseQuery):
    """
    Character's default objects.
    """
    table_name = "default_objects"

    @classmethod
    def get(cls, character):
        """
        Get character's default objects.

        Args:
            character: (string) character's key.
        """
        return WorldData.get_table_data(cls.table_name, character=character)
