
import threading
import importlib
import inspect
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from django.conf import settings
from muddery.server.database.engines import get_engine
from muddery.server.utils.logger import logger
from muddery.server.utils.singleton import Singleton


class DBManager(Singleton):
    """
    Database manager.
    """
    def __init__(self):
        self.engines = {}
        self.sessions = {}

    def connect(self):
        """
        Create db connections.
        """
        for key, cfg in settings.AL_DATABASES.items():
            try:
                engine = get_engine(cfg["ENGINE"], cfg)
                self.engines[key] = engine
                self.sessions[key] = Session(engine)
            except Exception as e:
                logger.log_trace("Can not connect to db.")
                raise e

    def create_tables(self):
        """
        Create database tables if they are not exist.
        """
        for key, cfg in settings.AL_DATABASES.items():
            try:
                engine = self.engines[key]
                module = importlib.import_module(cfg["MODELS"])
                tables = [cls for cls in vars(module).values() if inspect.isclass(cls)]
                for table in tables:
                    getattr(table, "__table__").create(engine, checkfirst=True)

            except Exception as e:
                logger.log_trace("Can not connect to db.")
                raise e

    def get_session(self, scheme):
        """
        The session of the database connection.
        """
        return self.sessions.get(scheme)

    def get_tables(self, scheme):
        """
        Get all tables' names of a scheme.
        """
        tables = []
        if scheme in settings.AL_DATABASES:
            module = importlib.import_module(settings.AL_DATABASES[scheme]["MODELS"])
            tables = [cls.__tablename__ for cls in vars(module).values() if inspect.isclass(cls)]

        return tables

    def clear_table(self, scheme, table_name):
        """
        clear all data in a table.
        """
        # get model
        session = self.sessions.get(scheme)
        if not session:
            return

        config = settings.AL_DATABASES[scheme]
        module = importlib.import_module(config["MODELS"])
        model = getattr(module, table_name)
        stmt = delete(model)
        try:
            result = session.execute(stmt)
            if result.rowcount > 0:
                session.commit()
        except Exception as e:
            session.rollback()

    def get_model(self, scheme, table_name):
        """
        Get the table's ORM model.
        """
        if scheme in settings.AL_DATABASES:
            config = settings.AL_DATABASES[scheme]
            module = importlib.import_module(config["MODELS"])
            model = getattr(module, table_name)
            return model
