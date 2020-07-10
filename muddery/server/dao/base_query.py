"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class BaseQuery(object):
    """
    Base data query.
    """

    # Set table's name here.
    table_name = ""

    @classmethod
    def get_fields(cls):
        """
        Get record fields.
        """
        return WorldData.get_fields(cls.table_name)

    @classmethod
    def all(cls):
        """
        Get all data.
        """
        return WorldData.get_table_all(cls.table_name)
