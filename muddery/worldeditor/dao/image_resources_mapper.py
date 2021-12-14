"""
Query and deal common tables.
"""

from muddery.server.utils.singleton import Singleton
from muddery.worldeditor.dao.common_mapper_base import CommonMapper


class ImageResourcesMapper(CommonMapper, Singleton):
    """
    Object's image.
    """
    def __init__(self):
        super(ImageResourcesMapper, self).__init__("image_resources")

    def get(self, resource):
        """
        Get object's image.

        Args:
            resource: (string) resource's path.
        """
        return self.get({
            "resource": resource
        })

    def add(self, path, type, width, height):
        """
        Add a new image record.

        Args:
            path: image's path
            type: image's type
            width: image's width
            height: image's height

        Return:
            none
        """
        self.update_or_add({
            "resource": path,
            "type": type,
        }, {
            "image_width": width,
            "image_height": height,
        })
