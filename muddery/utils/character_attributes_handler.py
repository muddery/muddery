"""
Handles characters attributes.
"""

from muddery.utils.localized_strings_handler import _
from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.data_sets import DATA_SETS


class CharacterAttributesHandler(object):
    """
    Handles character attribute's information.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.clear()

    def clear(self):
        """
        Clear data.
        """
        self.fields = {}
        self.keys = {}

    def reload(self):
        """
        Reload local string data.
        """
        self.clear()

        # Load localized string model.
        try:
            for record in DATA_SETS.character_attributes.objects.all():
                # Add db fields to dict.
                values = {"field": record.field,
                          "key": record.key,
                          "name": record.name,
                          "desc": record.desc}
                self.fields[record.field] = values
                self.keys[record.field] = values
        except Exception, e:
            print("Can not load character attribute: %s" % e)

    def has_field(self, field):
        """
        Check if object has this field.
        """
        return field in self.fields

    def has_key(self, key):
        """
        Check if object has this key.
        """
        return key in self.keys

    def for_field(self, field):
        """
        Get the attribute information for this field.
        """
        return self.fields.get(field, None)

    def for_key(self, key):
        """
        Get the attribute information for this key.
        """
        return self.keys.get(key, None)

# character attribute handler
CHARACTER_ATTRIBUTES_HANDLER = CharacterAttributesHandler()
