"""
Load and cache all worlddata.
"""

import importlib
from django.conf import settings
from sqlalchemy import UniqueConstraint
from muddery.server.database.manager import Manager
from muddery.server.utils.exception import MudderyError

_GA = object.__getattribute__
_SA = object.__setattr__


class RecordData(object):
    """
    Record object.
    """
    def __init__(self, fields, data):
        object.__setattr__(self, "_fields", fields)
        object.__setattr__(self, "_records", data)

    def __getattribute__(self, attr_name):
        try:
            pos = object.__getattribute__(self, "_fields")[attr_name]
        except KeyError:
            raise AttributeError("Can not find field %s." % attr_name)
        return object.__getattribute__(self, "_records")[pos]

    def __setattr__(self, attr_name, value):
        raise Exception("Cannot assign directly to record attributes!")

    def __delattr__(self, attr_name):
        raise Exception("Cannot delete record attributes!")


class MemoryTableAl(object):
    """
    Load and cache a table's data.
    """

    def __init__(self, session, model_path, model_name):
        self.model_name = model_name
        module = importlib.import_module(model_path)
        self.model = getattr(module, model_name)
        self.columns = self.model.__table__.columns.keys()
        self.session = Manager.instance().get_session(session)

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
        records = self.session.query(self.model).all()
        for r in records:
            row_data = [getattr(r, field_name) for field_name in self.columns]
            self.records.append(RecordData(self.table_fields, row_data))

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
        if type(self.model.__table_args__) == tuple:
            for table_args in self.model.__table_args__:
                if type(table_args) == dict and "index_together" in table_args:
                    indexes.extend(table_args["index_together"])
                if type(table_args) == UniqueConstraint:
                    indexes.append(table_args.columns.keys())
        elif type(self.model.__table_args__) == dict:
            if "index_together" in self.model.__table_args__:
                indexes.extend(self.model.__table_args__["index_together"])

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
            raise MudderyError("Only indexed fields can be searched, can not find %s's %s" % (self.table_name, index_name))

        index = self.index[index_name]

        if values in index:
            return [self.records[i] for i in index[values]]
        else:
            return []
