"""
Query and deal common tables.
"""

from muddery.server.database.dao.base_query import BaseQuery
from muddery.server.database.dao.worlddata import WorldData


class LocalizedStrings(BaseQuery):
    """
    All localized strings.
    """
    table_name = "localized_strings"

    @classmethod
    def get(cls, origin, category=""):
        """
        Get all data.
        """
        return WorldData.get_table_data(cls.table_name, category=category, origin=origin)
