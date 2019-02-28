"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from django.db import transaction


class SystemDataMapper(object):
    """
    The world editor system's data.
    """
    def __init__(self):
        self.model_name = "system_data"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

        if self.objects.count() == 0:
            data = self.model()
            data.full_clean()
            data.save()

    def get_object_index(self):
        """
        Increase the object index and get the new value.
        """
        record = self.objects.select_for_update().first()
        record.object_index += 1
        value = record.object_index
        record.save()
        return value


SYSTEM_DATA = SystemDataMapper()

