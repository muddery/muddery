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
        Reload data to local storage.
        """
        cls.clear()

        all_models = apps.get_models(settings.WORLD_DATA_APP)
        for model_obj in all_models:
            name = model_obj.__name__
            cls.tables[name] = TableData(name)

    @classmethod
    def get_table_all(cls, table_name):
        if table_name not in cls.tables:
            raise MudderyError("Can not find this table: %s" % table_name)

        fields = cls.tables[table_name].get_fields()
        records = cls.tables[table_name].all_data()
        return fields, records

    @classmethod
    def get_table_data(cls, table_name, key_field, value):
        """
        Get records from a table whose key field is the value.

        Args:
            table_name: (string) table's name
            key_field: (string, tuple of strings) field to filter
            value: field's value
        """
        if table_name not in cls.tables:
            raise MudderyError("Can not find this table: %s" % table_name)

        fields = cls.tables[table_name].get_fields()
        records = cls.tables[table_name].filter_data(key_field, value)
        return fields, records

    @classmethod
    def get_tables_data(cls, tables, key_field, value):
        """
        Get a record from tables whose key field is the value.
        Only can get one record.

        Args:
            tables: (list) tables' name
            key_field: (string, tuple of strings) field to filter
            value: field's value
        """
        fields = []
        record = []
        for table_name in tables:
            if table_name not in cls.tables:
                raise MudderyError("Can not find this table: %s" % table_name)

            records = cls.tables[table_name].filter_data(key_field, value)

            if not records:
                continue

            if len(records) > 1:
                raise MudderyError("Can not solve more than one records from table: %s" % table_name)

            fields.append(cls.tables[table_name].get_fields())
            record.append(records[0])

        return fields, [record]
