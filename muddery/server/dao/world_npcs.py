"""
Query and deal common tables.
"""

from muddery.server.dao.base_query import BaseQuery


class WorldNPCs(BaseQuery):
    """
    All NPCs whose position is fixed.
    """
    table_name = "world_npcs"
