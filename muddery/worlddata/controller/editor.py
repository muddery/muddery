"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.apps import apps
from django.conf import settings
from evennia.utils import logger
from muddery.utils.localized_strings_handler import _
from muddery.worlddata.processer import request_mapping
from muddery.worlddata.type_field import TypeField


@request_mapping
def query_type_tables(args):
    """
    Query all tables that contain custom types.
    """
    app = apps.get_app_config(settings.WORLD_DATA_APP)
    models = {}
    for model in app.get_models():
        fields = []
        for field in model._meta.get_fields():
            if isinstance(field, TypeField):
                fields.append(field.name)
                
        if fields:
            models[model._meta.object_name] = fields;

    return 0, models
