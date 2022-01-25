"""
Key value storage in relational database with write back memory cache.
"""

from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage
from muddery.server.database.storage.transaction import Transaction


class StorageWithCache(BaseKeyValueStorage):
    """
    The storage of object attributes.
    """
    def __init__(self, storage: BaseKeyValueStorage, cache: BaseKeyValueStorage):
        super(StorageWithCache, self).__init__()

        self.storage = storage
        self.cache = cache
        self.all_cached = False

    async def add(self, category: str, key: str, value: any = None) -> None:
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        async with self.lock:
            await self.storage.add(category, key, value)

            try:
                await self.cache.add(category, key, value)
            except KeyError:
                await self.set_category_cache(category)

    async def save(self, category: str, key: str, value: any = None) -> None:
        """
        Set a value to the default value field.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        async with self.lock:
            await self.storage.save(category, key, value)

            try:
                await self.cache.save(category, key, value)
            except KeyError:
                await self.set_category_cache(category)

    async def has(self, category: str, key: str, check_category: bool = False) -> bool:
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
            check_category: if check_category is True and does not has the category, it will raise a KeyError.
        """
        async with self.lock:
            try:
                return await self.cache.has(category, key, check_category=True)
            except KeyError:
                category_data = await self.set_category_cache(category)
                return key in category_data

    async def all(self) -> dict:
        """
        Get all data.
        :return:
        """
        async with self.lock:
            if self.all_cached:
                return await self.cache.load_all()
            else:
                return await self.set_all_cache()

    async def load(self, category: str, key: str, *default, for_update=False) -> any:
        """
        Get the value of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        async with self.lock:
            try:
                return await self.cache.load(category, key)
            except KeyError:
                category_data = await self.set_category_cache(category)
                try:
                    return category_data[key]
                except KeyError as e:
                    if len(default) > 0:
                        return default[0]
                    else:
                        raise e

    async def load_category(self, category: str, *default) -> dict:
        """
        Get all default field's values of a category.

        Args:
            category: (string) category's name.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `category`.
        """
        async with self.lock:
            try:
                return await self.cache.load_category(category)
            except KeyError:
                category_data = await self.set_category_cache(category)
                if category_data is not None:
                    return category_data
                else:
                    if len(default) > 0:
                        return default[0]
                    else:
                        raise KeyError

    async def delete(self, category: str, key: str) -> dict:
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.

        Return:
            (dict): deleted values
        """
        async with self.lock:
            await self.storage.delete(category, key)
            return await self.cache.delete(category, key)

    async def delete_category(self, category: str) -> dict:
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.

        Return:
            (dict): deleted values
        """
        async with self.lock:
            await self.storage.delete_category(category)
            return await self.cache.delete_category(category)

    async def set_all_cache(self) -> dict:
        """
        Load all data from db if have not loaded this category.
        :return:
        """
        all_data = await self.storage.load_all()
        await self.cache.set_all(all_data)
        self.all_cached = True
        return all_data

    async def set_category_cache(self, category: str) -> dict:
        """
        Load a category's data from db if have not loaded this category.
        :param category:
        :return:
        """
        try:
            data = await self.storage.load_category(category)
        except KeyError:
            data = {}

        await self.cache.set_category(category, data)
        return data

    def transaction_enter(self):
        self.storage.transaction_enter()
        self.cache.transaction_enter()

    def transaction_success(self, exc_type, exc_value, trace) -> None:
        self.storage.transaction_success(exc_type, exc_value, trace)
        self.cache.transaction_success(exc_type, exc_value, trace)

    def transaction_failed(self, exc_type, exc_value, trace) -> None:
        # Remove dirty caches.
        self.storage.transaction_failed(exc_type, exc_value, trace)
        self.cache.transaction_failed(exc_type, exc_value, trace)
