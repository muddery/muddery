"""
Query and deal common tables.
"""

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from muddery.utils import defines
from muddery.worlddata.dao.common_mapper_base import ObjectsMapper


class PropertiesDictMapper(object):
    """
    Object properties dict.
    """
    def __init__(self):
        self.model_name = "properties_dict"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get_properties(self, typeclass):
        """
        Get properties' information of the object.

        Args:
            typeclass: (string) typeclass's key.
        """
        return self.objects.filter(typeclass=typeclass)

    def get_property_info(self, typeclass, property):
        """
        Get a property's information.

        Args:
            typeclass: (string) typeclass's key.
            property: (string) property's key.
        """
        return self.objects.get(typeclass=typeclass, key=property)


PROPERTIES_DICT = PropertiesDictMapper()
