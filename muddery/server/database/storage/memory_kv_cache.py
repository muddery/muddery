"""
Key value storage in relational database.
"""

from muddery.server.database.storage.memory_kv_storage import MemoryKVStorage
from muddery.server.utils.exception import MudderyError, ERR


class MemoryKVCache(MemoryKVStorage):
    """
    The storage of object attributes.
    """
    def __init__(self):
        super(MemoryKVCache, self).__init__()

        self.in_transaction = False

        # used in transactions, record which category is changed.
        self.dirty_categories = set()

    async def add(self, category, key, value=None):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        await super(MemoryKVCache, self).add(category, key, value)

        if self.in_transaction:
            self.dirty_categories.add(category)

    async def save(self, category, key, value=None):
        """
        Set a value to the default value field.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        await super(MemoryKVCache, self).save(category, key, value)

        if self.in_transaction:
            self.dirty_categories.add(category)

    async def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        await super(MemoryKVCache, self).delete(category, key)

        if self.in_transaction:
            self.dirty_categories.add(category)

    async def set_all(self, all_data: dict) -> None:
        """
        Set all data.
        """
        await super(MemoryKVCache, self).set_all(all_data)

        if self.in_transaction:
            self.dirty_categories.update(self.storage.keys())

    async def set_category(self, category: str, data: dict) -> None:
        """
        Set a category of data to cache.
        """
        await super(MemoryKVCache, self).set_category(category, data)

        if self.in_transaction:
            self.dirty_categories.add(category)

    async def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        await super(MemoryKVCache, self).delete_category(category)

        if self.in_transaction:
            self.dirty_categories.add(category)

    def transaction_enter(self):
        self.dirty_categories = set()
        self.in_transaction = True

    def transaction_success(self, exc_type, exc_value, trace) -> None:
        self.dirty_categories = set()
        self.in_transaction = False

    def transaction_failed(self, exc_type, exc_value, trace) -> None:
        # Remove dirty caches.
        for category in self.dirty_categories:
            del self.storage[category]

        self.dirty_categories = set()
        self.in_transaction = False
