"""
Query and deal common tables.
"""

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from muddery.server.database.worlddata_models import common_objects


def get_model(model_name):
    """
    Get a model by name.
    """
    return apps.get_model(settings.WORLD_DATA_APP, model_name)


def get_all_models():
    """
    Query all models information.
    """
    app_config = apps.get_app_config(settings.WORLD_DATA_APP)
    return app_config.get_models()
