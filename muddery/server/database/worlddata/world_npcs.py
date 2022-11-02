"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.base_query import BaseQuery


class WorldNPCs(BaseQuery):
    """
    All NPCs whose position is fixed.
    """
    table_name = "world_npcs"

    @classmethod
    def get_location(cls, location):
        """
        Get all NPCs in the room.
        """
        return WorldData.get_table_data(cls.table_name, location=location)
