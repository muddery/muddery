"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings


class SkillsMapper(object):
    """
    Skills data.
    """
    objects = apps.get_model(settings.WORLD_DATA_APP, "skills").objects

    @classmethod
    def get_all(self):
        """
        Get all types.
        """
        return self.objects.all()
