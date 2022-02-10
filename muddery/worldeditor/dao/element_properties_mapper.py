"""
Query and deal common tables.
"""

from muddery.common.utils.singleton import Singleton
from muddery.worldeditor.dao.common_mapper_base import CommonMapper


class ElementPropertiesMapper(CommonMapper, Singleton):
    """
    Object's properties.
    """
    def __init__(self):
        super(ElementPropertiesMapper, self).__init__("element_properties")

    def get_properties(self, element_type, element_key, level):
        """
        Get object's properties.

        Args:
            element_type: (string) element's type.
            element_key: (string) element's key.
            level: (number) object's level.
        """
        return self.filter({
            "element": element_type,
            "key": element_key,
            "level": level,
        })

    def get_properties_all_levels(self, element_type, element_key):
        """
        Get object's properties.

        Args:
            element_type: (string) the element's type.
            element_key: (string) the element's key.
        """
        return self.filter({
            "element": element_type,
            "key": element_key
        }, order=["level"])

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
            self.update_or_add({
                    "element": element_type,
                    "key": element_key,
                    "level": level,
                    "property": prop,
            }, {"value": value})

    def delete_properties(self, element_type, element_key, level):
        """
        Delete object's properties.

        Args:
            element_type: (string) the element's type
            element_key: (string) the element's key.
            level: (number) object's level.
        """
        return self.delete({
            "element": element_type,
            "key": element_key,
            "level": level,
        })
