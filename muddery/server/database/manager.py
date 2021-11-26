
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from django.conf import settings
from muddery.server.utils.logger import game_server_logger as logger


class Manager(object):
    """
    Database manager.
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
        if not hasattr(Manager, "_instance"):
            with Manager._instance_lock:
                if not hasattr(Manager, "_instance"):
                    Manager._instance = Manager()
        return Manager._instance

    def __init__(self):
        self.engines = {}
        self.sessions = {}

    def create(self):
        """
        Create db connections.
        """
        for key, cfg in settings.AL_DATABASES.items():
            try:
                engine = create_engine(cfg["PROTOCOL"] + cfg["NAME"] + "?check_same_thread=False", echo=True)
                session = sessionmaker(bind=engine)

                self.engines[key] = engine
                self.sessions[key] = session()
            except Exception as e:
                logger.log_trace("Can not connect to db.")
                raise(e)

    def get_session(self, scheme):
        """
        The session of the database connection.
        """
        return self.sessions.get(scheme)
