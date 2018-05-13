"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings
from muddery.utils.utils import is_child


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


def get_objects_models():
    """
    Query all objects' models information.
    """
    app_config = apps.get_app_config(settings.WORLD_DATA_APP)
    models = [model for model in app_config.get_models() if is_child(model, BaseObjects)]
    return models


