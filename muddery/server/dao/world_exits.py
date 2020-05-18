"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class WorldExits(object):
    """
    All exits in the world.
    """
    table_name = "world_exits"

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)
