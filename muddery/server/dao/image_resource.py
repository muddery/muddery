
from muddery.server.dao.worlddata import WorldData


class ImageResource(object):
    """
    Equipment positions data.
    """
    table_name = "image_resources"

    @classmethod
    def get(cls, resource_path):
        """
        Get image's information by resource's path.
        """
        return WorldData.get_table_data(cls.table_name, "resource", resource_path)
