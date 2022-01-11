
import threading
import traceback
from muddery.server.conf import settings
from muddery.server.utils.utils import class_from_path
from muddery.server.utils.singleton import Singleton
from muddery.server.service.command_handler import CommandHandler
from muddery.server.database.db_manager import DBManager


class Server(Singleton):
    """
    The game world.
    """
    _instance_lock = threading.Lock()

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
        self.connect_db()

        self.create_the_world()
        self.create_command_handler()

    def connect_db(self):
        """
        Create the db connection.
        """
        if self.db_connected:
            return

        try:
            DBManager.inst().connect()
            DBManager.inst().create_tables()
            self.db_connected = True
        except Exception as e:
            traceback.print_exc()
            raise

    def create_the_world(self):
        """
        Create the whole game world.
        :return:
        """
        if self._world:
            return

        try:
            from muddery.server.mappings.element_set import ELEMENT
            world = ELEMENT("WORLD")()
            world.setup_element("")
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

        session_cmdset = class_from_path(settings.SESSION_CMDSET)
        account_cmdset = class_from_path(settings.ACCOUNT_CMDSET)
        character_cmdset = class_from_path(settings.CHARACTER_CMDSET)
        self._command_handler = CommandHandler(session_cmdset, account_cmdset, character_cmdset)

    async def handler_message(self, session, message):
        """
        Get a message from a session.
        """
        await self._command_handler.handler_command(session, message)
