"""
This model translates default strings into localized strings.
"""

from sqlalchemy import select, update, delete
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata_db import WorldDataDB
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.dao import general_querys


class CommonMapper(object):
    """
    Common data mapper.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.session = WorldDataDB.inst().get_session()
        self.model = WorldDataDB.inst().get_model(model_name)

    def all(self):
        stmt = select(self.model)
        result = self.session.execute(stmt)
        return result.scalars().all()

    def get(self, condition, for_update=False):
        """
        Get a record with conditions in kwargs.
        """
        stmt = select(self.model)

        if for_update:
            stmt = stmt.with_for_update()

        for field, value in condition.items():
            stmt = stmt.where(getattr(self.model, field) == value)

        result = self.session.execute(stmt)
        return result.scalars().one()

    def filter(self, condition, order=(), for_update=False):
        """
        Get a list of records with conditions in kwargs.
        """
        stmt = select(self.model)

        if for_update:
            stmt = stmt.with_for_update()

        for field, value in condition.items():
            stmt = stmt.where(getattr(self.model, field) == value)

        if order:
            stmt = stmt.order_by(*order)

        result = self.session.execute(stmt)
        return result.scalars().all()

    def count(self, condition):
        """
        Count the number of records with conditions in kwargs.
        """
        return general_querys.count(self.model_name, condition)

    def add(self, values):
        """
        Update or insert a record.
        """
        record = self.model(**values)
        self.session.add(record)
        self.session.flush()

    def update_or_add(self, condition, values):
        """
        Update or insert a record.
        """
        stmt = update(self.model).values(**values)
        for field, value in condition.items():
            stmt = stmt.where(getattr(self.model, field) == value)

        result = self.session.execute(stmt)

        if result.rowcount == 0:
            # Can not find the record to update, insert a new record.
            data = dict(condition, **values)
            record = self.model(**data)
            self.session.add(record)
            self.session.flush()

    def delete(self, condition):
        stmt = delete(self.model)
        for field, value in condition.items():
            stmt = stmt.where(getattr(self.model, field) == value)

        self.session.execute(stmt)


class ElementsMapper(CommonMapper):
    """
    Object data's mapper.
    """
    def __init__(self, element_type):
        element_class = ELEMENT(element_type)
        super(ElementsMapper, self).__init__(element_class.model_name)

        self.base_model_name = element_class.get_base_model()

    def all_with_base(self):
        """
        Get all records with its base data.
        """
        if self.base_model_name == self.model_name:
            return general_querys.get_all_from_tables([self.model_name])
        else:
            return general_querys.get_all_from_tables([self.base_model_name, self.model_name])

    def get_by_key_with_base(self, key):
        """
        Get a record with its base data.

        Args:
            key: (string) object's key.
        """
        if self.base_model_name == self.model_name:
            return general_querys.get_tables_record_by_key([self.model_name], key)
        else:
            return general_querys.get_tables_record_by_key([self.base_model_name, self.model_name], key)
