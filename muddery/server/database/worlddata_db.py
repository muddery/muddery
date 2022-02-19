
from muddery.common.database.db_manager import DBManager
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger


class WorldDataDB(DBManager):
    """
    Database manager.
    """
    def __init__(self):
        super(WorldDataDB, self).__init__(SETTINGS.WORLDDATA_DB, logger)
