
"""
Query and deal game data.
"""

from django.conf import settings
from muddery.server.utils import utils


class BaseData(object):
    """
    The base class of game data.
    """
    __table_name = ""
    __category_name = ""
    __key_field = ""
    __default_value_field = ""

    def __init__(self):
        # data storage

        self.storage = self.create_storage()

    def create_storage(self):
        """
        Create the storage object.
        """
        storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
        session = settings.GAME_DATA_APP
        config = settings.AL_DATABASES[session]
        return storage_class(
            session,
            config["MODELS"],
            self.__table_name,
            self.__category_name,
            self.__key_field,
            self.__default_value_field
        )
