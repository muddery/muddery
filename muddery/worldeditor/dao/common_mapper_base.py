"""
This model translates default strings into localized strings.
"""

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from muddery.worldeditor.dao.general_query_mapper import get_all_from_tables, get_tables_record_by_key

class CommonMapper(object):
    """
    Common data mapper.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = apps.get_model(settings.WORLD_DATA_APP, model_name)
        self.objects = self.model.objects

    def all(self):
        return self.objects.all()

    def get(self, *args, **kwargs):
        return self.objects.get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self.objects.filter(*args, **kwargs)


class ObjectsMapper(CommonMapper):
    """
    Object data's mapper.
    """
    def __init__(self, model_name):
        super(ObjectsMapper, self).__init__(model_name)

    def all_with_base(self):
        """
        Get all records with its base data.
        """
        return get_all_from_tables(["objects", self.model_name])

    def get_by_key_with_base(self, key):
        """
        Get a record with its base data.

        Args:
            key: (string) object's key.
        """
        return get_tables_record_by_key(["objects", self.model_name], key)
