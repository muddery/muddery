
"""
Query and deal game data.
"""

from muddery.server.settings import SETTINGS
from muddery.common.utils import utils
from muddery.server.database.storage.storage_with_cache import StorageWithCache
from muddery.server.database.gamedata_db import GameDataDB


class BaseData(object):
    """
    The base class of game data.
    """
    __table_name = None
    __category_name = None
    __key_field = None
    __default_value_field = None

    def __init__(self):
        # data storage
        self.storage = None

    async def init(self):
        """
        Init the object after created.
        """
        pass

    def create_storage(self, table_name, category_name, key_field, default_value_field):
        """
        Create the storage object.
        """
        storage_class = utils.class_from_path(SETTINGS.DATABASE_STORAGE_OBJECT)
        storage = storage_class(
            GameDataDB.inst().get_session(),
            SETTINGS.GAMEDATA_DB["MODELS"],
            table_name,
            category_name,
            key_field,
            default_value_field
        )

        cache_class = utils.class_from_path(SETTINGS.DATABASE_CACHE_OBJECT)
        cache = cache_class()

        return StorageWithCache(storage, cache)

    def create_storage_no_cache(self, table_name, category_name, key_field, default_value_field):
        """
        Create the storage object.
        """
        storage_class = utils.class_from_path(SETTINGS.DATABASE_STORAGE_OBJECT)
        return storage_class(
            GameDataDB.inst().get_session(),
            SETTINGS.GAMEDATA_DB["MODELS"],
            table_name,
            category_name,
            key_field,
            default_value_field
        )

    def transaction(self):
        """
        Guarantee the transaction execution of a given block.
        """
        return self.storage.transaction()
