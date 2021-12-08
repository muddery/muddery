"""
Key value storage in relational database.
"""
import traceback
import importlib
from django.conf import settings
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.utils import class_from_path
from muddery.server.database.manager import Manager


class KeyValueTableAl(BaseKeyValueStorage):
    """
    The storage of object attributes.
    """
    def __init__(self, session, model_path, model_name, category_field, key_field, default_value_field=None):
        """

        :param model_name: table's model
        :param category_field: category's field name in the table
        :param key_field: key's field name in the table
        :param default_value_field: default value's field name in the table.
                If set the default value field, it can only store a simple value.
                If the default value field is not set, value should be a dict.
        """
        super(KeyValueTableAl, self).__init__()

        # db model
        self.model_name = model_name
        module = importlib.import_module(model_path)
        self.model = getattr(module, model_name)
        self.columns = self.model.__table__.columns.keys()
        self.session = Manager.instance().get_session(session)

        exclude_fields = set()
        self.category_field = category_field
        if category_field:
            exclude_fields.add(category_field)

        self.key_field = key_field
        if key_field:
            exclude_fields.add(key_field)

        self.default_value_field = default_value_field
        if default_value_field:
            exclude_fields.add(default_value_field)

    def __del__(self):
        self.session.close()

    def add(self, category, key, value=None):
        """
        Add a new attribute. If the key already exists, raise an exception.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        if value is None:
            data = {}
        elif self.default_value_field is None:
            data = value
        else:
            data = {self.default_value_field: value}

        if self.category_field:
            data[self.category_field] = category

        if self.key_field:
            data[self.key_field] = key

        record = self.model(**data)
        self.session.add(record)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def save(self, category, key, value=None):
        """
        Set a value to the default value field.

        Args:
            category: (string) the category of data.
            key: (string) the key.
            value: (any) data.
        """
        if value is None:
            data = {}
        elif self.default_value_field is None:
            data = value
        else:
            data = {self.default_value_field: value}

        query = self.session.query(self.model)

        if self.category_field:
            query = query.filter(getattr(self.model, self.category_field) == category)

        if self.key_field:
            query = query.filter(getattr(self.model, self.key_field) == key)

        try:
            record = query.one()
            for key, value in data.items():
                setattr(record, key, value)
        except NoResultFound:
            if self.category_field:
                data[self.category_field] = category

            if self.key_field:
                data[self.key_field] = key

            record = self.model(**data)
            self.session.add(record)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        query = self.session.query(self.model)

        if self.category_field:
            query = query.filter(getattr(self.model, self.category_field) == category)

        if self.key_field:
            query = query.filter(getattr(self.model, self.key_field) == key)

        return query.count() > 0

    def all(self):
        """
        Get all data.
        :return:
        """
        query = self.session.query(self.model)
        records = query.all()

        all_data = {}
        if self.category_field:
            for r in records:
                category = getattr(r, self.category_field)
                if category not in all_data:
                    all_data[category] = {}

                key = getattr(r, self.key_field) if self.key_field else ""
                all_data[category][key] = {k: getattr(r, k) for k in self.columns}
        elif self.key_field:
            all_data[""] = {
                getattr(r, self.key_field): {
                    k: getattr(r, k) for k in self.columns
                } for r in records
            }
        elif len(records) > 0:
            all_data[""][""] = {k: getattr(records[0], k) for k in self.columns}
        else:
            all_data[""][""] = {}

        if self.default_value_field is not None:
            all_data = {
                key: value[self.default_value_field] for category, data in all_data.items() for key, value in data.items()
            }

        return all_data

    def load(self, category, key, *default):
        """
        Get the default field value of a key.

        Args:
            category: (string) the category of data.
            key: (string) data's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        query = self.session.query(self.model)

        if self.category_field:
            query = query.filter(getattr(self.model, self.category_field) == category)

        if self.key_field:
            query = query.filter(getattr(self.model, self.key_field) == key)

        try:
            record = query.one()
        except NoResultFound:
            if len(default) > 0:
                return default[0]
            else:
                raise KeyError

        if self.default_value_field is not None:
            return getattr(record, self.default_value_field)
        else:
            return {
                k: getattr(record, k) for k in self.columns
            }

    def load_category(self, category, *default):
        """
        Get all default field's values of a category.

        Args:
            category: (string) category's name.
        """
        query = self.session.query(self.model)

        if self.category_field:
            query = query.filter(getattr(self.model, self.category_field) == category)

        records = query.all()

        if len(records) == 0:
            if len(default) > 0:
                return default[0]
            else:
                raise KeyError

        if self.key_field:
            data = {
                getattr(record, self.key_field): {
                    k: getattr(record, k) for k in self.columns
                } for record in records
            }
        else:
            data = {
                "": {
                    k: getattr(record, k) for k in self.columns
                } for record in records
            }

        return data

    def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        query = self.session.query(self.model)

        if self.category_field:
            query = query.filter(getattr(self.model, self.category_field) == category)

        if self.key_field:
            query = query.filter(getattr(self.model, self.key_field) == key)

        query.delete()
        self.session.commit()

    def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        query = self.session.query(self.model)

        if self.category_field:
            query = query.filter(getattr(self.model, self.category_field) == category)

        query.delete()
        self.session.commit()

    def atomic(self):
        """
        Guarantee the atomic execution of a given block.
        """
        return
