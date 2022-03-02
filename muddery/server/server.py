import traceback
from muddery.server.settings import SETTINGS
from muddery.common.utils.utils import class_from_path
from muddery.common.utils.singleton import Singleton
from muddery.server.service.command_handler import CommandHandler
from muddery.server.database.gamedata_db import GameDataDB
from muddery.server.database.worlddata_db import WorldDataDB
from muddery.common.utils.utils import classes_in_path
from muddery.server.database.gamedata.base_data import BaseData


class Server(Singleton):
    """
    The game world.
    """
    class ClassProperty:
        def __init__(self, method):
            self.method = method

        def __get__(self, instance, owner):
            return self.method(owner)

    def __init__(self, *args, **kwargs):
        self.configs = {}
        self._world = None
        self._command_handler = None
        self.db_connected = False

    async def init(self):
        await self.connect_db()
        await self.create_the_world()
        self.create_command_handler()

    async def connect_db(self):
        """
        Create the db connection.
        """
        if self.db_connected:
            return

        try:
            WorldDataDB.inst().connect()
            GameDataDB.inst().connect()
        except Exception as e:
            traceback.print_exc()
            raise

        # load classes
        for cls in classes_in_path(SETTINGS.PATH_GAMEDATA_DAO, BaseData):
            await cls.inst().init()

        self.db_connected = True

    async def create_the_world(self):
        """
        Create the whole game world.
        :return:
        """
        if self._world:
            return

        try:
            from muddery.server.mappings.element_set import ELEMENT
            world = ELEMENT("WORLD")()
            await world.setup_element("")
            self._world = world
        except Exception as e:
            traceback.print_exc()
            raise

    @ClassProperty
    def world(cls):
        """
        A system_data store. Everything stored to this is from the
        world data. It will be reset every time when the object init .
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.system.attr = value etc.
        """
        return cls.inst()._world

    def create_command_handler(self):
        """
        Create and init the command handler.
        """
        if self._command_handler:
            return

        session_cmdset = class_from_path(SETTINGS.SESSION_CMDSET)
        account_cmdset = class_from_path(SETTINGS.ACCOUNT_CMDSET)
        character_cmdset = class_from_path(SETTINGS.CHARACTER_CMDSET)
        self._command_handler = CommandHandler(session_cmdset, account_cmdset, character_cmdset)

    def parse_command(self, raw_string):
        """
        Parse JSON formatted command.
        """
        return self._command_handler.parse_command(raw_string)

    async def handler_command(self, session, key, args):
        """
        Get a command from a session.
        """
        await self._command_handler.handler_command(session, key, args)
