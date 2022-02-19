
import importlib
import inspect
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy import inspect as sql_inspect
from muddery.common.database.engines import get_engine, get_db_link
from muddery.common.utils.singleton import Singleton


class DBManager(Singleton):
    """
    Database manager.
    """
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.engine = None
        self.session = None
        self.connected = False

    def connect(self):
        """
        Create db connections.
        """
        if self.connected:
            return

        try:
            self.engine = get_engine(self.config["ENGINE"], self.config)
            self.session = Session(self.engine, autocommit=True)
        except Exception as e:
            self.logger.log_trace("Can not connect to db.")
            raise e

        self.connected = True

    def create_tables(self):
        """
        Create database tables if they are not exist.
        """
        try:
            module = importlib.import_module(self.config["MODELS"])
            tables = [cls for cls in vars(module).values() if inspect.isclass(cls) and hasattr(cls, "__table__")]
            for table in tables:
                getattr(table, "__table__").create(self.engine, checkfirst=True)
        except Exception as e:
            self.logger.log_trace("Can not connect to db.")
            raise e

    def check_tables(self):
        """
        Check if all database tables exist.
        """
        try:
            table_names = sql_inspect(self.engine).get_table_names()
        except Exception as e:
            self.logger.log_trace("Can not connect to db.")
            raise e

        return len(table_names) > 0

    def get_db_link(self):
        """
        The session of the database connection.
        """
        return get_db_link(self.config["ENGINE"], self.config)

    def get_engine(self):
        """
        The session of the database connection.
        """
        return self.engine

    def get_session(self):
        """
        The session of the database connection.
        """
        return self.session

    def get_tables(self):
        """
        Get all tables' names of a scheme.
        """
        module = importlib.import_module(self.config["MODELS"])
        return [cls.__tablename__ for cls in vars(module).values()
               if inspect.isclass(cls) and hasattr(cls, "__tablename__")]

    def clear_table(self, table_name):
        """
        clear all data in a table.
        """
        # get model
        module = importlib.import_module(self.config["MODELS"])
        model = getattr(module, table_name)
        stmt = delete(model)
        self.session.execute(stmt)

    def get_model(self, table_name):
        """
        Get the table's ORM model.
        """
        module = importlib.import_module(self.config["MODELS"])
        model = getattr(module, table_name)
        return model
