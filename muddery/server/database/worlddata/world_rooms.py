"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class WorldRooms(BaseQuery):
    """
    All rooms in the world.
    """
    table_name = "world_rooms"

    @classmethod
    def get_by_area(cls, area):
        """
        Get rooms of the the area.
        """
        return WorldData.get_table_data(cls.table_name, area=area)
