
from muddery.common.database.db_manager import DBManager
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.utils.logger import logger


class WorldEditorDB(DBManager):
    """
    Database manager.
    """
    def __init__(self):
        super(WorldEditorDB, self).__init__(SETTINGS.WORLDEDITOR_DB, logger)
