"""
The base class of key value storage.
"""

from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage


class BaseKeyValueCache(BaseKeyValueStorage):
    """
    The storage of key-values.
    """
    async def set_all(self, all_data: dict) -> None:
        """
        Set all data to cache.
        """
        pass

    async def set_category(self, category: str, data: dict) -> None:
        """
        Set a category of data to cache.
        """
        pass

    async def has_category(self, category: str) -> bool:
        """
        Check if the category is in cache.
        """
        pass
