"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class IconResourcesMapper(object):
    """
    Object's icons.
    """
    def __init__(self):
        self.model_name = "icon_resources"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get(self, resource):
        """
        Get object's icon.

        Args:
            resource: (string) icon resource's path.
        """
        return self.objects.get(resource=resource)

    def add(self, path, width, height):
        """
        Add a new icon record.

        Args:
            path: icon's path
            width: icon's width
            height: icon's height

        Return:
            none
        """
        record = {
            "resource": path,
            "image_width": width,
            "image_height": height,
        }

        data = self.model(**record)
        data.full_clean()
        data.save()


ICON_RESOURCES = IconResourcesMapper()

