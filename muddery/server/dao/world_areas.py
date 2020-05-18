"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class WorldAreas(object):
    """
    All areas in the game world.
    """
    table_name = "world_areas"

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)
