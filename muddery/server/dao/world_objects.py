"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class WorldObjects(object):
    """
    All objects whose position is fixed.
    """
    table_name = "world_objects"

    @classmethod
    def all(cls):
        """
        Get a NPC's shops.
        """
        return WorldData.get_table_all(cls.table_name)
