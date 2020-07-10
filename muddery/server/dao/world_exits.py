"""
Query and deal common tables.
"""

from muddery.server.dao.base_query import BaseQuery


class WorldExits(BaseQuery):
    """
    All exits in the world.
    """
    table_name = "world_exits"
