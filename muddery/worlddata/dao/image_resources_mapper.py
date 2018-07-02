"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class ImageResourcesMapper(object):
    """
    Object's image.
    """
    def __init__(self):
        self.model_name = "image_resources"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get(self, resource):
        """
        Get object's image.

        Args:
            resource: (string) resource's path.
        """
        return self.objects.get(resource=resource)

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
        record = {
            "resource": path,
            "type": type,
            "image_width": width,
            "image_height": height,
        }

        data = self.model(**record)
        data.full_clean()
        data.save()


IMAGE_RESOURCES = ImageResourcesMapper()

