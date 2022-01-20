"""
Load and cache all worlddata.
"""

import importlib
from sqlalchemy import UniqueConstraint, select
from muddery.server.database.db_manager import DBManager
from muddery.server.utils.exception import MudderyError
from muddery.server.database.storage.memory_record import MemoryRecord


class MemoryTable(object):
    """
    Load and cache a table's data.
    """

    def __init__(self, session_name, model_path, model_name):
        self.model_name = model_name
        module = importlib.import_module(model_path)
        self.model = getattr(module, model_name)
        self.columns = self.model.__table__.columns.keys()
        self.session = DBManager.inst().get_session(session_name)

        self.records = []
        self.table_fields = {}
        self.index = {}     # index: {field's value: recode's index}
        self.reload()

    def clear(self):
        self.records = []
        self.table_fields = {}
        self.index = {}

    def reload(self):
        self.clear()

        for i, field_name in enumerate(self.columns):
            self.table_fields[field_name] = i

        # load records
        stmt = select(self.model)
        result = self.session.execute(stmt)
        records = result.scalars()
        for r in records:
            row_data = [getattr(r, field_name) for field_name in self.columns]
            self.records.append(MemoryRecord(self.table_fields, row_data))

        # set unique index
        for field_name in self.columns:
            if field_name != "id" and self.model.__table__.columns[field_name].unique:
                self.index[field_name] = dict((getattr(record, field_name), [i]) for i, record in enumerate(self.records))

        # set common index
        for field_name in self.columns:
            if field_name != "id" and self.model.__table__.columns[field_name].index:
                all_values = {}
                for i, record in enumerate(self.records):
                    key = getattr(record, field_name)
                    if key in all_values:
                        all_values[key].append(i)
                    else:
                        all_values[key] = [i]
                self.index[field_name] = all_values

        # index together or unique together
        indexes = []

        if hasattr(self.model, "__index_together__"):
            indexes.extend(self.model.__index_together__)

        if type(self.model.__table_args__) == tuple:
            for table_args in self.model.__table_args__:
                if type(table_args) == UniqueConstraint:
                    indexes.append(table_args.columns.keys())

        for set_fields in indexes:
            index_fields = sorted(set_fields)
            all_values = {}
            for i, record in enumerate(self.records):
                keys = tuple(getattr(record, field_name) for field_name in set_fields)
                if keys in all_values:
                    all_values[keys].append(i)
                else:
                    all_values[keys] = [i]
            index_name = ".".join(index_fields)
            self.index[index_name] = all_values

    def fields(self):
        """
        Get table fields.
        """
        return self.table_fields

    def all(self):
        """
        Get all data.
        """
        return [record for i, record in enumerate(self.records)]

    def first(self):
        """
        Get the first record.
        """
        if len(self.records) > 0:
            return self.records[0]

    def get(self, record_id):
        """
        Get data by record's id.
        """
        if 0 <= record_id < len(self.records):
            return self.records[record_id]

    def filter(self, **conditions):
        """
        Filter data by record's value. Fields must have index. If filter multi fields, put them in a tuple.

        Args:
            kwargs: (dict) query conditions
        """
        if len(conditions) == 0:
            return self.all()

        if len(conditions) == 1:
            keys = list(conditions.keys())
            index_name = keys[0]
            values = conditions[index_name]
        else:
            unique_fields = sorted(set(conditions.keys()))
            index_name = ".".join(unique_fields)
            values = tuple(conditions[field_name] for field_name in unique_fields)

        if index_name not in self.index:
            raise MudderyError("Only indexed fields can be searched, can not find %s's %s" % (self.model_name, index_name))

        index = self.index[index_name]

        if values in index:
            return [self.records[i] for i in index[values]]
        else:
            return []
