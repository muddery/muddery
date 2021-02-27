"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery


class WorldObjects(BaseQuery):
    """
    All objects whose position is fixed.
    """
    table_name = "world_objects"
