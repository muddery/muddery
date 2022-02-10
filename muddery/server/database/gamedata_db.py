
from muddery.common.database.db_manager import DBManager
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger


class GameDataDB(DBManager):
    """
    Database manager.
    """
    def __init__(self):
        super(GameDataDB, self).__init__(SETTINGS.GAMEDATA_DB, logger)
