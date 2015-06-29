"""
Object key handler.
"""

from django.conf import settings
from django.db.models.loading import get_model


class ObjectKeyHandler(object):
    """
    The model maintains a table of key->model.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.clear()


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

        model_names = [model for data_models in settings.WORLD_DATA_MODELS
                       for model in data_models]

        for model_name in model_names:
            try:
                model_obj = get_model(settings.WORLD_DATA_APP, model_name)
                for record in model_obj.objects.all():
                    self.key_model[record.key] = model_name
            except Exception, e:
                pass

    
    def add_key(self, key, model):
        """
        Add a key.
        """
        self.key_model[key] = model


    def remove_key(self, key):
        """
        Remove a key.
        """
        del self.key_model[key]


    def get_model(self, key):
        """
        Get key's model.
        """
        if not key in self.key_model:
            return

        return self.key_model[key]


# main dialoguehandler
OBJECT_KEY_HANDLER = ObjectKeyHandler()
