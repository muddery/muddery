"""
Query and deal common tables.
"""

from muddery.server.dao.base_query import BaseQuery


class WorldRooms(object):
    """
    All rooms in the world.
    """
    table_name = "world_rooms"
