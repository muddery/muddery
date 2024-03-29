"""
Load and cache all worlddata.
"""
import importlib
import inspect
import traceback
from muddery.common.utils.exception import MudderyError
from muddery.server.settings import SETTINGS
from muddery.server.database.storage.memory_record import MemoryRecord
from muddery.server.database.storage.memory_table import MemoryTable
from muddery.server.database.worlddata_db import WorldDataDB


class WorldData(object):
    """
    Load and cache all worlddata.
    """
    tables = {}

    @classmethod
    def clear_all(cls):
        """
        Clear data.
        """
        cls.tables = {}

    @classmethod
    def reload_all(cls):
        """
        Reload data to the local storage.
        """
        cls.clear_all()

        module = importlib.import_module(SETTINGS.WORLD_DATA_MODEL_FILE)
        models = [cls for cls in vars(module).values() if inspect.isclass(cls)]
        for model in models:
            config = SETTINGS.DATABASES[SETTINGS.WORLD_DATA_APP]
            cls.tables[model.__name__] = MemoryTable(
                SETTINGS.WORLD_DATA_APP,
                config["MODELS"],
                model.__name__)

    @classmethod
    def refresh(cls, table_name):
        """
        Clear data.
        """
        if table_name in cls.tables:
            del cls.tables[table_name]

    @classmethod
    def load_table(cls, table_name):
        """
        Load a table to the local storage.
        """
        try:
            config = SETTINGS.WORLDDATA_DB
            cls.tables[table_name] = MemoryTable(
                WorldDataDB.inst().get_session(),
                config["MODELS"],
                table_name)
        except Exception as e:
            raise MudderyError("Can not load table %s: %s" % (table_name, e))

    @classmethod
    def get_fields(cls, table_name):
        if table_name not in cls.tables:
            cls.load_table(table_name)

        return cls.tables[table_name].fields()

    @classmethod
    def get_table_all(cls, table_name):
        if table_name not in cls.tables:
            cls.load_table(table_name)

        return cls.tables[table_name].all()

    @classmethod
    def get_first_data(cls, table_name):
        if table_name not in cls.tables:
            cls.load_table(table_name)

        return cls.tables[table_name].first()

    @classmethod
    def get_table_data(cls, table_name, **condition):
        """
        Get records from a table whose fields matches the condition.

        Args:
            table_name: (string) table's name
            condition: (dict) query conditions
        """
        if table_name not in cls.tables:
            cls.load_table(table_name)

        return cls.tables[table_name].filter(**condition)

    @classmethod
    def get_tables_data(cls, tables, key):
        """
        Get a record from tables whose key field is the value.
        Only can get one record.

        Args:
            tables: (list) tables' name
            key: (string) object's key

        Return:
            (list) records
        """
        all_fields = {}
        row_data = []
        for table_name in tables:
            if table_name not in cls.tables:
                cls.load_table(table_name)

            fields = cls.tables[table_name].fields()
            records = cls.tables[table_name].filter(key=key)
            field_pos = dict(zip(fields, range(len(row_data), len(row_data) + len(fields))))

            if not records:
                all_fields.update(field_pos)
                row_data.extend([None] * len(fields))
            elif len(records) > 1:
                raise MudderyError("Can not solve more than one records from table: %s" % table_name)
            else:
                record = records[0]
                all_fields.update(field_pos)
                row_data.extend([getattr(record, field_name) for field_name in fields])

        return [MemoryRecord(all_fields, row_data)]
