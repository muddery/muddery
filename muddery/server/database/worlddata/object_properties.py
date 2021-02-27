"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class ObjectProperties(BaseQuery):
    """
    Object's properties.
    """
    table_name = "object_properties"

    @classmethod
    def get_properties(cls, obj_key, level):
        """
        Get object's properties.

        Args:
            obj_key: (string) object's key.
            level: (number) object's level.
        """
        return WorldData.get_table_data(cls.table_name, object=obj_key, level=level)
