"""
Query and deal common tables.
"""

import importlib
from django.conf import settings
from django.core.exceptions import ValidationError
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.database.manager import Manager


class ElementPropertiesMapper(object):
    """
    Object's properties.
    """
    def __init__(self):
        self.model_name = "element_properties"
        session_name = settings.WORLD_DATA_MODEL_FILE
        self.session = Manager.instance().get_session(session_name)

        config = settings.AL_DATABASES[session_name]
        module = importlib.import_module(config["MODELS"])
        self.model = getattr(module, self.model_name)

    def get_properties(self, element_type, element_key, level):
        """
        Get object's properties.

        Args:
            element_type: (string) element's type.
            element_key: (string) element's key.
            level: (number) object's level.
        """
        return self.objects.filter(element=element_type, key=element_key, level=level)

    def get_properties_all_levels(self, element_type, element_key):
        """
        Get object's properties.

        Args:
            element_type: (string) the element's type.
            element_key: (string) the element's key.
        """
        return self.objects.filter(element=element_type, key=element_key).order_by("level")

    def add_properties(self, element_type, element_key, level, values):
        """
        Add object's properties.

        Args:
            element_type: (string) the element's type
            element_key: (string) the element's key.
            level: (number) object's level.
            values: (dict) values to save.
        """
        # import values
        for prop, value in values.items():
            records = self.objects.filter(element=element_type, key=element_key, level=level, property=prop)
            if records:
                # Update.
                records.update(value=value)
            else:
                # Create.
                record = {
                    "element": element_type,
                    "key": element_key,
                    "level": level,
                    "property": prop,
                    "value": value
                }
                data = self.model(**record)
                data.save()

    def delete_properties(self, element_type, element_key, level):
        """
        Delete object's properties.

        Args:
            element_type: (string) the element's type
            element_key: (string) the element's key.
            level: (number) object's level.
        """
        return self.objects.filter(element=element_type, key=element_key, level=level).delete()


ELEMENT_PROPERTIES = ElementPropertiesMapper()
