"""
Load and cache all worlddata.
"""

from django.conf import settings
from django.apps import apps
from muddery.server.utils.exception import MudderyError

_GA = object.__getattribute__
_SA = object.__setattr__


class RecordData(object):
    """
    Record object.
    """
    def __init__(self, fields, data):
        self._fields = fields
        self._records = data

    def __getattribute__(self, attr_name):
        return self._records[self._fields(attr_name)]

    def __setattr__(self, attr_name, value):
        raise Exception("Cannot assign directly to record attributes!")

    def __delattr__(self, attr_name):
        raise Exception("Cannot delete record attributes!")


class TableData(object):
    """
    Load and cache a table's data.
    """

    def __init__(self, table_name):
        self.table_name = table_name

        self.data = []
        self.fields = {}
        self.index = {}
        self.reload()

    def clear(self):
        self.data = []
        self.fields = {}
        self.index = {}

    def reload(self):
        self.clear()

        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.table_name)
        fields = [field.name for field in model_obj._meta.fields]
        for i, field_name in enumerate(fields):
            self.fields[field_name] = i

        # load records
        records = model_obj.objects.all()
        for record in records:
            row_data = [record.serializable_value(field_name) for field_name in fields]
            self.data.append(RecordData(self.fields, row_data))

        # set unique index
        for field in model_obj._meta.fields:
            if field.unique:
                pos = self.fields[field.name]
                self.index[field.name] = {(record[pos], [i]) for i, record in enumerate(self.data)}

        # set common index
        for field in model_obj._meta.fields:
            if field.db_index:
                pos = self.fields[field.name]
                all = {}
                for i, record in enumerate(self.data):
                    key = record[pos]
                    if key in all:
                        all[key].append(i)
                    else:
                        all[key] = [i]
                self.index[field.name] = all

        # unique together
        if model_obj._meta.unique_together:
            unique_fields = model_obj._meta.unique_together
            pos = [self.fields[field_name] for field_name in unique_fields]
            all = {}
            for i, record in enumerate(self.data):
                keys = (record[p] for p in pos)
                all[keys] = i
            self.index[unique_fields] = all

    def get_fields(self):
        """
        Get table fields.
        """
        return self.fields

    def all_data(self):
        """
        Get all data.
        """
        return self.data

    def get_data(self, record):
        """
        Get data by record's id.
        """
        if 0 <= record < len(self.data):
            return self.data[record]

    def filter_data(self, key_field, value):
        """
        Filter data by record's value. Fields must have index. If filter multi fields, put them in a tuple.

        Args:
            key_field: (string, tuple of strings) field to filter
            value: field's value
        """
        if key_field not in self.index:
            raise MudderyError("Only indexed fields can be searched.")

        index = self.index[key_field]
        if value in index:
            return [self.data[i] for i in index[value]]
        else:
            return []
