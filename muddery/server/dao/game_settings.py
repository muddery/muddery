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
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)
