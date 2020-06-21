"""
Load and cache all worlddata.
"""

from django.conf import settings
from django.apps import apps
from muddery.server.dao.tabledata import TableData
from muddery.server.utils.exception import MudderyError


class WorldData(object):
    """
    Load and cache all worlddata.
    """
    tables = {}

    @classmethod
    def clear(cls):
        """
        Clear data.
        """
        cls.tables = {}

    @classmethod
    def reload(cls):
        """
        Reload data to the local storage.
        """
        cls.clear()

        all_models = apps.get_models(settings.WORLD_DATA_APP)
        for model_obj in all_models:
            name = model_obj.__name__
            cls.tables[name] = TableData(name)

    @classmethod
    def load_table(cls, table_name):
        """
        Load a table to the local storage.
        """
        try:
            model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
            name = model_obj.__name__
            cls.tables[name] = TableData(name)
        except Exception as e:
            raise MudderyError("Can not load table %s: %s" % (table_name, e))

    @classmethod
    def get_table_all(cls, table_name):
        if table_name not in cls.tables:
            cls.load_table(table_name)

        return cls.tables[table_name].all_data()

    @classmethod
    def get_table_data(cls, table_name, **kwargs):
        """
        Get records from a table whose key field is the value.

        Args:
            table_name: (string) table's name
            kwargs: (dict) query conditions
        """
        if table_name not in cls.tables:
            cls.load_table(table_name)

        return cls.tables[table_name].filter_data(**kwargs)

    @classmethod
    def get_tables_data(cls, tables, **kwargs):
        """
        Get a record from tables whose key field is the value.
        Only can get one record.

        Args:
            tables: (list) tables' name
            kwargs: (dict) query conditions
        """
        records = []
        for table_name in tables:
            if table_name not in cls.tables:
                cls.load_table(table_name)

            records = cls.tables[table_name].filter_data(**kwargs)

            if not records:
                continue

            if len(records) > 1:
                raise MudderyError("Can not solve more than one records from table: %s" % table_name)

            records.append(records[0])

        return records
