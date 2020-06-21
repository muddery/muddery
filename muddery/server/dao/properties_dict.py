"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class PropertiesDict(object):
    """
    Object properties dict.
    """
    table_name = "properties_dict"

    @classmethod
    def get_properties(cls, typeclass):
        """
        Get properties by typeclass's name.
        """
        return WorldData.get_table_data(cls.table_name, typeclass=typeclass)
