"""
Key value storage in relational database.
"""

import importlib
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import select, update, delete
from sqlalchemy import func
from muddery.server.database.storage.base_kv_storage import BaseKeyValueStorage


class TableKVStorage(BaseKeyValueStorage):
    """
    The storage of object attributes.
    """
    def __init__(self,
                 session: any,
                 model_path: str,
                 model_name: str,
                 category_field: str,
                 key_field: str,
                 default_value_field: str = None):
        """
        :param model_name: table's model
        :param category_field: category's field name in the table
        :param key_field: key's field name in the table
        :param default_value_field: default value's field name in the table.
                If set the default value field, it can only store a simple value.
                If the default value field is not set, value should be a dict.
        """
        super(TableKVStorage, self).__init__()

        # db model
        self.session = session
        self.model_name = model_name
        module = importlib.import_module(model_path)
        self.model = getattr(module, model_name)
        self.columns = self.model.__table__.columns.keys()

        self.trans = None

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

    async def has(self, category: str, key: str, check_category: bool = False) -> bool:
        """
        Check if the key exists.

        Args:
            category: the category of data.
            key: attribute's key.
            check_category: if check_category is True and does not has the category, it will raise a KeyError.
        """
        stmt = select(func.count()).select_from(self.model)

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        if self.key_field:
            stmt = stmt.where(getattr(self.model, self.key_field) == key)

        result = self.session.execute(stmt)
        count = result.scalars().one()
        if count > 0:
            return True

        if not check_category:
            return False

        # Check if the category exists.
        if not self.category_field:
            return False

        stmt = select(func.count()).select_from(self.model).where(getattr(self.model, self.category_field) == category)
        result = self.session.execute(stmt)
        count = result.scalars().one()
        if count > 0:
            return False
        else:
            raise KeyError


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

    async def set_all(self, all_data: dict) -> None:
        """
        Set all data to the storage.
        """
        with self.session.begin():
            # remove old data
            stmt = delete(self.model)
            self.session.execute(stmt)

            for cate_name, cate_data in all_data.items():
                for key_name, key_data in cate_data.items():
                    data = key_data
                    if self.category_field:
                        data[self.category_field] = cate_name
                    if self.key_field:
                        data[self.key_field] = key_name

                    record = self.model(**data)
                    self.session.add(record)

    async def load_all(self) -> dict:
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

    async def set_category(self, category: str, data: dict) -> None:
        """
        Set a category of data.
        """
        with self.session.begin():
            # remove old data
            stmt = delete(self.model)
            if self.category_field:
                stmt = stmt.where(getattr(self.model, self.category_field) == category)
            self.session.execute(stmt)

            for key_name, key_data in data.items():
                data = key_data
                if self.category_field:
                    data[self.category_field] = category
                if self.key_field:
                    data[self.key_field] = key_name

                record = self.model(**data)
                self.session.add(record)

    async def has_category(self, category: str) -> bool:
        """
        Check if the category exists.
        """
        stmt = select(func.count()).select_from(self.model)

        if self.category_field:
            stmt = stmt.where(getattr(self.model, self.category_field) == category)

        result = self.session.execute(stmt)
        record = result.scalars().one()
        return record > 0

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
            if self.default_value_field:
                data = {
                    getattr(record, self.key_field): getattr(record, self.default_value_field) for record in records
                }
            else:
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

    def transaction_enter(self) -> None:
        self.trans = self.session.begin()
        self.trans.__enter__()

    def transaction_success(self, exc_type, exc_value, trace) -> None:
        self.trans.__exit__(exc_type, exc_value, trace)
        self.trans = None

    def transaction_failed(self, exc_type, exc_value, trace) -> None:
        self.trans.__exit__(exc_type, exc_value, trace)
        self.trans = None
