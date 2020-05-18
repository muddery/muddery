"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class WorldNPCs(object):
    """
    All NPCs whose position is fixed.
    """
    table_name = "world_npcs"

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)
