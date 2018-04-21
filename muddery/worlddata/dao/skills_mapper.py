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
    model = apps.get_model(settings.WORLD_DATA_APP, "skills")
