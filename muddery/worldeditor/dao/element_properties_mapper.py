"""
Query and deal common tables.
"""

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from muddery.server.utils.exception import MudderyError, ERR


class ElementPropertiesMapper(object):
    """
    Object's properties.
    """
    def __init__(self):
        self.model_name = "element_properties"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def get_properties(self, object, level):
        """
        Get object's properties.

        Args:
            object: (string) object's key.
            level: (number) object's level.
        """
        return self.objects.filter(object=object, level=level)

    def get_properties_all_levels(self, object):
        """
        Get object's properties.

        Args:
            object: (string) object's key.
        """
        return self.objects.filter(object=object).order_by("level")

    def add_properties(self, object, level, values):
        """
        Add object's properties.

        Args:
            object: (string) object's key.
            level: (number) object's level.
            values: (dict) values to save.
        """
        # import values
        for prop, value in values.items():
            records = self.objects.filter(object=object, level=level, property=prop)
            if records:
                # Update.
                records.update(value=value)
            else:
                # Create.
                record = {
                    "object": object,
                    "level": level,
                    "property": prop,
                    "value": value
                }
                data = self.model(**record)
                data.save()

    def delete_properties(self, object, level):
        """
        Delete object's properties.

        Args:
            object: (string) object's key.
            level: (number) object's level.
        """
        return self.objects.filter(object=object, level=level).delete()


ELEMENT_PROPERTIES = ElementPropertiesMapper()
