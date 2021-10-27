"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery


class WorldChannels(BaseQuery):
    """
    All channels in the game world.
    """
    table_name = "world_channels"
