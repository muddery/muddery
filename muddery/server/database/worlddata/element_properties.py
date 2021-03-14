"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class ElementProperties(BaseQuery):
    """
    Object's properties.
    """
    table_name = "element_properties"

    @classmethod
    def get_properties(cls, element, key, level):
        """
        Get element's properties.

        Args:
            element: (string) element's type.
            key: (string) element's key
            level: (number) object's level.
        """
        return WorldData.get_table_data(cls.table_name, element=element, key=key, level=level)
