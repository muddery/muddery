"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class ImageResource(BaseQuery):
    """
    Image's data.
    """
    table_name = "image_resources"

    @classmethod
    def get(cls, resource_path):
        """
        Get image's information by resource's path.
        """
        return WorldData.get_table_data(cls.table_name, resource=resource_path)
