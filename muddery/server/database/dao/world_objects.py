"""
Query and deal common tables.
"""

from muddery.server.database.dao.base_query import BaseQuery


class WorldObjects(BaseQuery):
    """
    All objects whose position is fixed.
    """
    table_name = "world_objects"
