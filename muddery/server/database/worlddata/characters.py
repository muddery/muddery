"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class Characters(BaseQuery):
    """
    Object's properties.
    """
    table_name = "characters"

    @classmethod
    def get_data(cls, key):
        """
        Get the character's data.

        Args:
            key: (string) element's key
        """
        return WorldData.get_table_data(cls.table_name, key=key)
