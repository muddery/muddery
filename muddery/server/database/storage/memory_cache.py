"""
Object's attributes cache.
"""

from muddery.server.database.storage.base_object_storage import BaseObjectStorage


class MemoryCache(BaseObjectStorage):
    """
    Store attributes in db and using memory cache.
    """
    def __init__(self, model_name):
        # db model
        super(MemoryCache, self).__init__(model_name)
        self.cache = {}

    def save(self, obj_id, key, value):
        """
        Set an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            value: (any) attribute's value.
        """
        self.check_cache(obj_id)
        self.cache[obj_id][key] = value

        super(MemoryCache, self).save(obj_id, key, value)

    def saves(self, obj_id, value_dict):
        """
        Set attributes.

        Args:
            obj_id: (number) object's id.
            value_dict: (dict) a dict of key-values.
        """
        self.check_cache(obj_id)
        self.cache[obj_id].update(value_dict)

        super(MemoryCache, self).saves(obj_id, value_dict)

    def has(self, obj_id, key):
        """
        Check if the attribute exists.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        self.check_cache(obj_id)
        return key in self.cache[obj_id]

    def load(self, obj_id, key, *args):
        """
        Get the value of an attribute.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
            args: (any or none) default value.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        self.check_cache(obj_id)
        try:
            return self.cache[obj_id][key]
        except KeyError:
            if len(args) > 0:
                return args[0]
            else:
                raise AttributeError

    def delete(self, obj_id, key):
        """
        delete an attribute of an object.

        Args:
            obj_id: (number) object's id.
            key: (string) attribute's key.
        """
        self.check_cache(obj_id)
        try:
            del self.cache[obj_id][key]
        finally:
            super(MemoryCache, self).delete(obj_id, key)

    def load_obj(self, obj_id):
        """
        Get all values of an object.

        Args:
            obj_id: (number) object's id.
        """
        self.check_cache(obj_id)
        return self.cache[obj_id]

    def remove_obj(self, obj_id):
        """
        Remove an object's all attributes.

        Args:
            obj_id: (number) object's id.
        """
        try:
            del self.cache[obj_id]
        finally:
            super(MemoryCache, self).remove_obj(obj_id)

    def check_cache(self, obj_id):
        """
        Load an object's data from db if have not loaded this object.
        :param obj_id:
        :return:
        """
        if obj_id not in self.cache:
            self.cache[obj_id] = super(MemoryCache, self).load_obj(obj_id)
