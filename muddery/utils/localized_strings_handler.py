"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from django.conf import settings
from django.apps import apps
from evennia.utils import logger


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

        # Get db model
        try:
            model_obj = apps.get_model(settings.WORLD_DATA_APP, settings.LOCALIZED_STRINGS_MODEL)
            for record in model_obj.objects.all():
                # Add db fields to dict.
                if (record.category, record.origin) in self.dict:
                    # origin words duplicated
                    print("************ WARNING ************")
                    print("Local string duplicated: \"%s:%s\"" % (record.category, record.origin))
                    continue
                self.dict[(record.category, record.origin)] = record.local
        except Exception, e:
            print("Can not load server local string: %s" % e)
            pass


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


# main dialoguehandler
LOCALIZED_STRINGS_HANDLER = LocalizedStringsHandler()


# translater
def LS(origin, category="", default=None):
    """
    This function returns the localized string.
    """
    return LOCALIZED_STRINGS_HANDLER.translate(origin, category, default)


