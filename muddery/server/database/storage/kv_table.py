"""
Key value storage in relational database.
"""
import traceback
import importlib
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import select, update, delete
from sqlalchemy import func
from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.utils import class_from_path
from muddery.server.database.db_manager import DBManager


class KeyValueTable(BaseKeyValueStorage):
    """
    The storage of object attributes.
    """
    def __init__(self, session_name, model_path, model_name, category_field, key_field, default_value_field=None):
        """

        :param model_name: table's model
        :param category_field: category's field name in the table
        :param key_field: key's field name in the table
        :param default_value_field: default value's field name in the table.
                If set the default value field, it can only store a simple value.
                If the default value field is not set, value should be a dict.
        """
        super(KeyValueTable, self).__init__()

        # db model
        self.model_name = model_name
        module = importlib.import_module(model_path)
        self.model = getattr(module, model_name)
        self.columns = self.model.__table__.columns.keys()
        self.session = DBManager.inst().get_session(session_name)

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

    async def add(self, category, key, value=None):
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

    async def save(self, category, key, value=None):
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

        stmt = update(self.model).values(**data)

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        if self.key_field:
            stmt = stmt.where(getattr(self.model, self.key_field) == key)

        result = self.session.execute(stmt)
        if result.rowcount == 0:
            # no matched rows
            if self.category_field:
                data[self.category_field] = category

            if self.key_field:
                data[self.key_field] = key

            record = self.model(**data)
            self.session.add(record)

    async def has(self, category, key):
        """
        Check if the key exists.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        stmt = select(func.count()).select_from(self.model)

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        if self.key_field:
            stmt = stmt.where(getattr(self.model, self.key_field) == key)

        result = self.session.execute(stmt)
        record = result.scalars().one()
        return record > 0

    async def all(self):
        """
        Get all data.
        :return:
        """
        stmt = select(self.model)
        result = self.session.execute(stmt)
        records = result.scalars().all()

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

    async def load(self, category, key, *default, for_update=False):
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
        stmt = select(self.model)

        if for_update:
            stmt = stmt.with_for_update()

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        if self.key_field:
            stmt = stmt.where(getattr(self.model, self.key_field) == key)

        result = self.session.execute(stmt)

        try:
            record = result.scalars().one()
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

    async def load_category(self, category, *default):
        """
        Get all default field's values of a category.

        Args:
            category: (string) category's name.
        """
        stmt = select(self.model)

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        result = self.session.execute(stmt)
        records = result.scalars().all()

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

        if len(data) == 0:
            if len(default) > 0:
                return default[0]
            else:
                raise KeyError

        return data

    async def delete(self, category, key):
        """
        delete a key.

        Args:
            category: (string) the category of data.
            key: (string) attribute's key.
        """
        stmt = delete(self.model)

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        if self.key_field:
            stmt = stmt.where(getattr(self.model, self.key_field) == key)

        self.session.execute(stmt)

    async def delete_category(self, category):
        """
        Remove all values of a category.

        Args:
            category: (string) the category of data.
        """
        stmt = delete(self.model)

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        self.session.execute(stmt)

    def transaction(self):
        """
        Guarantee the transaction execution of a given block.
        """
        return self.session.begin()
