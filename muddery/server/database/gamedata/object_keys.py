
"""
Store object's element key data in memory.
"""

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger


class ObjectKeys(object):
    """
    The storage of object keys.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = apps.get_model(settings.GAME_DATA_APP, model_name)
        self.records = {}
        self.key_object = {}
        self.unique_objects = {}

        # load data
        for record in self.model.objects.all():
            self.records[record.object_id] = {
                "key": record.object_key,
                "type": record.unique_type,
            }
            self.key_object[record.object_key] = record.object_id
            if record.unique_type not in self.unique_objects:
                self.unique_objects[record.unique_type] = {}
            self.unique_objects[record.unique_type][record.object_id] = record.object_key

    def add(self, object_id, object_key, unique_type=None):
        """
        Store an object's key.
        :param object_id:
        :param object_key:
        :param unique_type:
        :return:
        """
        if object_id in self.records:
            if self.records[object_id]["key"] == object_key and self.records[object_id]["type"] == unique_type:
                return

        try:
            record = self.model(
                object_id=object_id,
                object_key=object_key,
                unique_type=unique_type
            )
            record.save()

            self.records[object_id] = {
                "key": object_key,
                "type": unique_type,
            }
            self.key_object[object_key] = object_id
            if record.unique_type not in self.unique_objects:
                self.unique_objects[record.unique_type] = {}
            self.unique_objects[record.unique_type][object_id] = object_key
        except Exception as e:
            logger.log_err("Can not add %s %s's element key: %s" % (object_id, object_key, e))

    def remove(self, object_id):
        """
        Remove an object.
        :param object_id:
        :return:
        """
        if object_id not in self.records:
            return

        try:
            self.model.objects.get(object_id=object_id).delete()
            key = self.records[object_id]["key"]
            unique_type = self.records[object_id]["type"]
            del self.records[object_id]
            del self.key_object[key]
            del self.unique_objects[unique_type][object_id]
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            logger.log_err("Can not remove object's element key: %s %s" % (object_id, e))

    def get_key(self, object_id):
        """
        Get an object's element key.
        :param object_id:
        :return:
        """
        try:
            return self.records[object_id]["key"]
        except KeyError:
            return None

    def get_object_id(self, key):
        """
        Get an object by its element key.
        :param key:
        :return:
        """
        try:
            return self.key_object[key]
        except KeyError:
            return None

    def get_unique_objects(self, unique_type):
        """
        Get an object by its element key.
        :param key:
        :param unique_type:
        :return:
        """
        try:
            return self.unique_objects[unique_type]
        except KeyError:
            return {}


OBJECT_KEYS = ObjectKeys("object_keys")
