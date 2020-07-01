"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class GameSettings(object):
    """
    Game setting data.
    """
    table_name = "game_settings"

    @classmethod
    def get_fields(cls):
        """
        Get table fields.
        """
        return WorldData.get_fields(cls.table_name)

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)
