"""
Query and deal common tables.
"""

import importlib
from django.apps import apps
from django.conf import settings
from muddery.server.database.worlddata_models import common_objects


def get_model(model_name):
    """
    Get a model by name.
    """
    config = settings.AL_DATABASES[settings.WORLD_DATA_MODEL_FILE]
    module = importlib.import_module(config["MODELS"])
    return getattr(module, model_name)


def get_all_models():
    """
    Query all models information.
    """
    app_config = apps.get_app_config(settings.WORLD_DATA_APP)
    return app_config.get_models()
