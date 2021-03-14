"""
Load and cache all worlddata.
"""

from django.apps import apps
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
            raise AttributeError
        return object.__getattribute__(self, "_records")[pos]

    def __setattr__(self, attr_name, value):
        raise Exception("Cannot assign directly to record attributes!")

    def __delattr__(self, attr_name):
        raise Exception("Cannot delete record attributes!")


class MemoryTable(object):
    """
    Load and cache a table's data.
    """

    def __init__(self, data_app, table_name):
        self.records_app = data_app
        self.table_name = table_name
        self.model = apps.get_model(self.records_app, self.table_name)

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

        fields = [field.name for field in self.model._meta.fields]
        for i, field_name in enumerate(fields):
            self.table_fields[field_name] = i

        # load records
        records = self.model.objects.all()
        for record in records:
            row_data = [record.serializable_value(field_name) for field_name in fields]
            self.records.append(RecordData(self.table_fields, row_data))

        # set unique index
        for field in self.model._meta.fields:
            if field.name != "id" and field.unique:
                self.index[field.name] = dict((getattr(record, field.name), [i]) for i, record in enumerate(self.records))

        # set common index
        for field in self.model._meta.fields:
            if field.db_index:
                all_values = {}
                for i, record in enumerate(self.records):
                    key = getattr(record, field.name)
                    if key in all_values:
                        all_values[key].append(i)
                    else:
                        all_values[key] = [i]
                self.index[field.name] = all_values

        # index together
        for index_together in self.model._meta.index_together:
            index_fields = set(index_together)
            all_values = {}
            for i, record in enumerate(self.records):
                keys = tuple(getattr(record, field_name) for field_name in index_fields)
                if keys in all_values:
                    all_values[keys].append(i)
                else:
                    all_values[keys] = [i]
            index_name = ".".join(index_fields)
            self.index[index_name] = all_values

        # unique together
        for unique_together in self.model._meta.unique_together:
            unique_fields = set(unique_together)
            all_values = {}
            for i, record in enumerate(self.records):
                keys = tuple(getattr(record, field_name) for field_name in unique_fields)
                if keys in all_values:
                    all_values[keys].append(i)
                else:
                    all_values[keys] = [i]
            index_name = ".".join(unique_fields)
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

    def filter(self, **kwargs):
        """
        Filter data by record's value. Fields must have index. If filter multi fields, put them in a tuple.

        Args:
            kwargs: (dict) query conditions
        """
        if len(kwargs) == 0:
            return self.all()

        if len(kwargs) == 1:
            keys = list(kwargs.keys())
            index_name = keys[0]
            values = kwargs[index_name]
        else:
            unique_fields = set(kwargs.keys())
            index_name = ".".join(unique_fields)
            values = tuple(kwargs[field_name] for field_name in unique_fields)

        if index_name not in self.index:
            raise MudderyError("Only indexed fields can be searched.")

        index = self.index[index_name]

        if values in index:
            return [self.records[i] for i in index[values]]
        else:
            return []
