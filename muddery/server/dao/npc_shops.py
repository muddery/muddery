"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class NPCShops(object):
    """
    NPC's dialogue list.
    """
    table_name = "npc_shops"

    @classmethod
    def get(cls, npc_key):
        """
        Get a NPC's shops.
        """
        return WorldData.get_table_data(cls.table_name, "npc", npc_key)
