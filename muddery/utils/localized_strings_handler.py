"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from muddery.worlddata.data_sets import DATA_SETS


class LocalizedStringsHandler(object):
    """
    This model translates default strings into localized strings.
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
            for record in DATA_SETS.localized_strings.objects.all():
                # Add db fields to dict. Overwrite system localized strings.
                self.dict[(record.category, record.origin)] = record.local
        except Exception, e:
            print("Can not load custom localized string: %s" % e)

    def translate(self, origin, category="", default=None):
        """
        Translate origin string to local string.
        """
        try:
            # Get local string.
            local = self.dict[(category, origin)]
            if local:
                return local
        except:
            pass

        if default is None:
            # Else return origin string.
            return origin
        else:
            return default

# main dialogue handler
LOCALIZED_STRINGS_HANDLER = LocalizedStringsHandler()


# translator
def _(origin, category="", default=None):
    """
    This function returns the localized string.
    """
    return LOCALIZED_STRINGS_HANDLER.translate(origin, category, default)
