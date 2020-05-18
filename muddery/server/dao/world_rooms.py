"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class WorldRooms(object):
    """
    All rooms in the world.
    """
    table_name = "world_rooms"

    @classmethod
    def all(cls):
        """
        Get a NPC's shops.
        """
        return WorldData.get_table_all(cls.table_name)
