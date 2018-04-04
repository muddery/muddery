"""
Battle commands. They only can be used when a character is in a combat.
"""

from django.apps import apps
from django.conf import settings
from evennia.utils import logger
from muddery.utils.localized_strings_handler import _
from muddery.worlddata.processer import request_mapping


@request_mapping
def query_type_tables(args):
    """
    Query all tables that contain custom types.
    """
    worldata_app = apps.get_app_config(settings.WORLD_DATA_APP)

    return 0, "success"
