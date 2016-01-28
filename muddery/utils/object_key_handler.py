"""
Object key handler, stores key's model name.
"""

from django.conf import settings
from django.apps import apps


class ObjectKeyHandler(object):
    """
    The model maintains a table of key->model.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.key_model = {}

    def clear(self):
        """
        Clear data.
        """
        self.key_model = {}

    def reload(self):
        """
        Reload data.
        """
        self.clear()

        # Get model names.
        for model_name in settings.OBJECT_DATA_MODELS:
            try:
                model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
                for record in model_obj.objects.all():
                    # Add key's model name.
                    key = record.serializable_value("key")
                    if key not in self.key_model:
                        self.key_model[key] = []
                    self.key_model[key].append(model_name)
            except Exception, e:
                pass

    def get_models(self, key):
        """
        Get key's model.

        Args:
            key: the key of an object

        Returns:
            key's models
        """
        if key not in self.key_model:
            return []

        return self.key_model[key]


# main dialoguehandler
OBJECT_KEY_HANDLER = ObjectKeyHandler()
