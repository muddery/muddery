"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class HonourSettings(BaseQuery):
    """
    Game setting data.
    """
    table_name = "honour_settings"

    @classmethod
    def get_fields(cls):
        """
        Get table fields.
        """
        return WorldData.get_fields(cls.table_name)

    @classmethod
    def get_first_data(cls):
        """
        Get table fields.
        """
        return WorldData.get_first_data(cls.table_name)
