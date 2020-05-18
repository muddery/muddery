"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class LocalizedStrings(object):
    """
    All sentences in dialogues.
    """
    table_name = "localized_strings"

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)

    @classmethod
    def get(cls, origin, category=""):
        """
        Get all data.
        """
        return WorldData.get_table_data(cls.table_name, ("category", "origin"), (category, origin))
