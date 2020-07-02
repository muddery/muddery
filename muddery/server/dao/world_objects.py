"""
Query and deal common tables.
"""

from muddery.server.dao.base_query import BaseQuery


class WorldObjects(object):
    """
    All objects whose position is fixed.
    """
    table_name = "world_objects"
