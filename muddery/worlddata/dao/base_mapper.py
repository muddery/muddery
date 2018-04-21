"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings


class BaseMapper(object):
    """
    Base class of mappers.
    """
	model = None
	
	@classmethod
    def get_fields(cls):
        """
        Get all fields.
        """
        return cls.model._meta.fields

    @classmethod
    def get_all(cls):
        """
        Get all types.
        """
        return cls.model.objects.all()

