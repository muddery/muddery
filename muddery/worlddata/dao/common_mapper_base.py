"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from muddery.worlddata.dao.general_query_mapper import get_all_from_tables

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

    def get(self, **kwargs):
        return self.objects.get(**kwargs)

    def filter(self, **kwargs):
        return self.objects.filter(**kwargs)


class ObjectsMapper(CommonMapper):
    """
    Object data's mapper.
    """
    def __init__(self, model_name):
        super(ObjectsMapper, self).__init__(model_name)

    def all_base(self):
        """
        Get all records with its base data.
        """
        return get_all_from_tables(["objects", self.model_name])
