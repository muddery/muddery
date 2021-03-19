"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.base_query import BaseQuery


class WorldExits(BaseQuery):
    """
    All exits in the world.
    """
    table_name = "world_exits"

    @classmethod
    def get(cls, location):
        """
        Get a room's exits.
        """
        return WorldData.get_table_data(cls.table_name, location=location)
