"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class NPCShops(BaseQuery):
    """
    NPC's dialogue list.
    """
    table_name = "npc_shops"

    @classmethod
    def get(cls, npc_key):
        """
        Get a NPC's shops.
        """
        return WorldData.get_table_data(cls.table_name, npc=npc_key)
