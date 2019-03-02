"""
Query and deal common tables.
"""

from __future__ import print_function

from multiprocessing import Lock
from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from django.db import transaction


def load_object_index():
    model = apps.get_model(settings.WORLD_DATA_APP, "system_data")
    record = model.objects.select_for_update().first()
    return record.object_index


class SystemDataMapper(object):
    """
    The world editor system's data.
    """
    __lock = Lock()
    __object_index = load_object_index()

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
        self.__lock.acquire()
        self.__object_index += 1
        value = self.__object_index
        self.__lock.release()

        record = self.objects.first()
        record.object_index = value
        record.save()

        return value


SYSTEM_DATA = SystemDataMapper()

