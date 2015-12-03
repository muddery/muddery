"""
This model instantiate a script_handler.
"""

from evennia.utils.utils import class_from_module
from django.conf import settings


# load script handler from settings.SCRIPT_HANDLER
scriptclass = class_from_module(settings.SCRIPT_HANDLER)
SCRIPT_HANDLER = scriptclass()
