
"""
Store object's element key data in memory.
"""

import traceback
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.server.utils import utils


class ObjectKeys(object):
    """
    The storage of object keys.
    """
    def __init__(self, model_name):
        storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
        self.storage = storage_class(model_name, "", "object_id")

        # load data
        self.key_object = {}
        self.unique_objects = {}

        try:
            all_data = self.storage.load_category("", {})
            for object_id, info in all_data.items():
                self.key_object[info["object_key"]] = object_id
                if info["unique_type"]:
                    if info["unique_type"] not in self.unique_objects:
                        self.unique_objects[info["unique_type"]] = {}
                    self.unique_objects[info["unique_type"]][object_id] = info["object_key"]
        except KeyError:
            pass

    def save(self, object_id, object_key, unique_type=None):
        """
        Store an object's key.
        :param object_id:
        :param object_key:
        :param unique_type:
        :return:
        """
        self.storage.save("", object_id, {
            "object_key": object_key,
            "unique_type": unique_type
        })

        self.key_object[object_key] = object_id
        if unique_type:
            if unique_type not in self.unique_objects:
                self.unique_objects[unique_type] = {}
            self.unique_objects[unique_type][object_id] = object_key

    def delete(self, object_id):
        """
        Delete an object.
        :param object_id:
        :return:
        """
        traceback.print_stack()
        self.storage.delete("", object_id)

    def get_key(self, object_id):
        """
        Get an object's element key.
        :param object_id:
        :return:
        """
        try:
            info = self.storage.load("", object_id)
            return info["object_key"]
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
