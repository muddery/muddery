"""
This model translates default strings into localized strings.
"""

from django.conf import settings
from sqlalchemy import select, update, delete, func
from muddery.server.mappings.element_set import ELEMENT
from muddery.worldeditor.dao import general_query_mapper as query
from muddery.server.database.db_manager import DBManager


class CommonMapper(object):
    """
    Common data mapper.
    """
    def __init__(self, model_name):
        self.model_name = model_name

        session_name = settings.WORLD_DATA_APP
        self.session = DBManager.inst().get_session(session_name)
        self.model = DBManager.inst().get_model(session_name, model_name)

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
            stmt = stmt.order(*order)

        result = self.session.execute(stmt)
        return result.scalars().all()

    def count(self, condition):
        """
        Count the number of records with conditions in kwargs.
        """
        stmt = select(func.count()).select_from(self.model)
        for field, value in condition.items():
            stmt = stmt.where(getattr(self.model, field) == value)

        result = self.session.execute(stmt)
        return result.scalars().all()

    def add(self, values):
        """
        Update or insert a record.
        """
        record = self.model(**values)
        try:
            self.session.add(record)
        except Exception as e:
            self.session.roll_back()
            raise

    def update_or_add(self, condition, values):
        """
        Update or insert a record.
        """
        stmt = update(self.model)
        for field, value in condition.items():
            stmt = stmt.where(getattr(self.model, field) == value)

        try:
            result = self.session.execute(stmt)
        except Exception as e:
            self.session.roll_back()
            raise

        if result.rowcount == 0:
            # Can not found the record to update, insert a new record.
            data = dict(condition, **values)
            record = self.model(**data)
            try:
                self.session.add(record)
            except Exception as e:
                self.session.roll_back()
                raise

    def delete(self, condition):
        stmt = delete(self.model)
        for field, value in condition.items():
            stmt = stmt.where(getattr(self.model, field) == value)

        try:
            result = self.session.execute(stmt)
        except Exception as e:
            self.session.roll_back()
            raise


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
            return query.get_all_from_tables([self.model_name])
        else:
            return query.get_all_from_tables([self.base_model_name, self.model_name])

    def get_by_key_with_base(self, key):
        """
        Get a record with its base data.

        Args:
            key: (string) object's key.
        """
        if self.base_model_name == self.model_name:
            return query.get_tables_record_by_key([self.model_name], key)
        else:
            return query.get_tables_record_by_key([self.base_model_name, self.model_name], key)
