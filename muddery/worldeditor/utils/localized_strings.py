"""
This model translates default strings into localized strings.
"""

from muddery.common.utils.singleton import Singleton
from muddery.worldeditor.dao.common_mappers import LOCALIZED_STRINGS


class LocalizedStrings(Singleton):
    """
    This model translates default strings into localized strings.
    """
    def __init__(self):
        """
        Initialize handler
        """
        super(LocalizedStrings, self).__init__()

        self.loaded = False
        self.clear()

    def clear(self):
        """
        Clear data.
        """
        self.dict = {}

    def load(self):
        """
        Reload local string data.
        """
        self.clear()

        # Load localized string model.
        try:
            for record in LOCALIZED_STRINGS.all():
                # Add db fields to dict. Overwrite system localized strings.
                self.dict[(record.category, record.origin)] = record.local

            self.loaded = True
        except Exception as e:
            print("Can not load custom localized string: %s" % e)

    def trans(self, origin, category="", default=None):
        """
        Translate origin string to local string.
        """
        if not self.loaded:
            self.load()

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
