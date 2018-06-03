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

    def get(self, key):
        """
        Get object's image.

        Args:
            key: (string) object's key.
        """
        return self.objects.get(key=key)


IMAGE_RESOURCES = ImageResourcesMapper()

