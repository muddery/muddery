"""
This module defines available model types.
"""

from django.conf import settings
from importlib import import_module


class DataHandler(object):

    def __init__(self, settings_path):
        """
        Load data settings.

        Args:
            settings_path: (String) Data settings module's path.

        Returns:
            None.
        """
        settings_module = import_module(settings_path)

        self.SystemData = settings_module.SystemData()
        self.BasicData = settings_module.BasicData()
        self.ObjectsData = settings_module.ObjectsData()
        self.ObjectsAdditionalData = settings_module.ObjectsAdditionalData()
        self.OtherData = settings_module.OtherData()
        self.EventAdditionalData = settings_module.EventAdditionalData()


# Data handler
SYSTEM_DATA_HANDLER = DataHandler(settings.SYSTEM_DATA_SETTINGS)

DATA_HANDLER = DataHandler(settings.DATA_SETTINGS)
