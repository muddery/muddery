"""
Query and deal common tables.
"""

from muddery.server.dao.worlddata import WorldData


class DefaultObjects(object):
    """
    Character's default objects.
    """
    table_name = "default_objects"

    @classmethod
    def get(cls, character):
        """
        Get character's default objects.

        Args:
            character: (string) character's key.
        """
        return WorldData.get_table_data(cls.table_name, character=character)

