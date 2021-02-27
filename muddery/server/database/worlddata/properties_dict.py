"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class PropertiesDict(BaseQuery):
    """
    Object properties dict.
    """
    table_name = "properties_dict"

    @classmethod
    def get_properties(cls, element_type):
        """
        Get properties by element_type's name.
        """
        return WorldData.get_table_data(cls.table_name, element_type=element_type)
