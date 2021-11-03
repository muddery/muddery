"""
Query and deal common tables.
"""

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

        if self.model.objects.count() == 0:
            data = self.model()
            data.full_clean()
            data.save()

    def get_object_index(self):
        """
        Increase the object index and get the new value.
        """
        with transaction.atomic():
            record = self.objects.select_for_update().first()
            index = record.object_index
            record.object_index = index + 1
            record.save()

        return index


SYSTEM_DATA = SystemDataMapper()

