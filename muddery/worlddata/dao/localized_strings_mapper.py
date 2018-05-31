"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.apps import apps
from django.conf import settings


class LocalizedStringsMapper(object):
    """
    Localized strings.
    """
    def __init__(self):
        self.model_name = "localized_strings"
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects

    def all(self):
        """
        Get all localized strings.
        """
        return self.objects.all()

    def get(self, origin, category=""):
        """
        Get a localized string.

        Args:
            origin: (string) origin string.
            category: (string) local string's category.
        """
        return self.objects.filter(origin=origin, category=category)


LOCALIZED_STRINGS = LocalizedStringsMapper()

