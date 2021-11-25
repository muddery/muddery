
import threading
from django.conf import settings
from muddery.server.utils.utils import class_from_path
from muddery.server.service.command_handler import CommandHandler


class Server(object):
    """
    The game world.
    """
    _instance_lock = threading.Lock()

    class ClassProperty:
        def __init__(self, method):
            self.method = method

        def __get__(self, instance, owner):
            return self.method(owner)

    @classmethod
    def instance(cls, *args, **kwargs):
        """
        Singleton object.
        """
        if not hasattr(Server, "_instance"):
            with Server._instance_lock:
                if not hasattr(Server, "_instance"):
                    Server._instance = Server(*args, **kwargs)
        return Server._instance

    def __init__(self, *args, **kwargs):
        self._world = None
        self._command_handler = None

    def create_the_world(self):
        """
        Create the whole game world.
        :return:
        """
        from muddery.server.mappings.element_set import ELEMENT
        world = ELEMENT("WORLD")()
        world.setup_element("")
        self._world = world

    @ClassProperty
    def world(cls):
        """
        A system_data store. Everything stored to this is from the
        world data. It will be reset every time when the object init .
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.system.attr = value etc.
        """
        return cls.instance()._world

    def create_command_handler(self):
        """
        Create and init the command handler.
        """
        session_cmdset = class_from_path(settings.SESSION_CMDSET)
        account_cmdset = class_from_path(settings.ACCOUNT_CMDSET)
        character_cmdset = class_from_path(settings.CHARACTER_CMDSET)
        self._command_handler = CommandHandler(session_cmdset, account_cmdset, character_cmdset)

    def handler_message(self, session, message):
        """
        Get a message from a session.
        """
        self._command_handler.handler_command(session, message)

