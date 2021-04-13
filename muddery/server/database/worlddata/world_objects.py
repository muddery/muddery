"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.base_query import BaseQuery


class WorldObjects(BaseQuery):
    """
    All objects whose position is fixed.
    """
    table_name = "world_objects"

    @classmethod
    def get_location(cls, location):
        """
        Get a room's exits.
        """
        return WorldData.get_table_data(cls.table_name, location=location)
