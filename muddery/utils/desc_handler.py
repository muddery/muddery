"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from muddery.worlddata.data_sets import DATA_SETS


class DescHandler(object):
    """
    This model stores all descriptions on all conditions.
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
        self.dict = {}

    def reload(self):
        """
        Reload local string data.
        """
        self.clear()

        # Load localized string model.
        try:
            for record in DATA_SETS.condition_desc.objects.all():
                # Add db fields to dict.
                if not self.dict.has_key(record.key):
                    self.dict[record.key] = []
                self.dict[record.key].append({"key": record.key,
                                              "condition": record.condition,
                                              "desc": record.desc})
        except Exception, e:
            print("Can not load description: %s" % e)

    def get(self, key):
        """
        Get specified descriptions.
        """
        return self.dict.get(key, None)

# main description handler
DESC_HANDLER = DescHandler()
