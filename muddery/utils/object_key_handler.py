"""
Object key handler, stores key's model name.
"""

from muddery.worlddata.data_sets import DATA_SETS


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
        data_settings_list = []
        data_settings_list.extend(DATA_SETS.object_data)
        data_settings_list.extend(DATA_SETS.object_additional_data)
        for data_settings in data_settings_list:
            try:
                for record in data_settings.objects.all():
                    # Add key's model name.
                    key = record.serializable_value("key")
                    if key not in self.key_model:
                        self.key_model[key] = []
                    self.key_model[key].append(data_settings.model_name)
            except Exception, e:
                pass

    def get_models(self, key):
        """
        Get key's model.

        Args:
            key: (string) the key of an object

        Returns:
            (list) key's models' name
        """
        if key not in self.key_model:
            return []

        return self.key_model[key]

    def has_key(self, key):
        """
        Check if this key exists.

        Args:
            key: (string) the key of an object

        Returns:
            (boolean) result
        """
        return key in self.key_model


# main object key's handler
OBJECT_KEY_HANDLER = ObjectKeyHandler()
