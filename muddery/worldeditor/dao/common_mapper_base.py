"""
This model translates default strings into localized strings.
"""

import importlib
from django.conf import settings
from muddery.server.mappings.element_set import ELEMENT
from muddery.worldeditor.dao import general_query_mapper as q
from muddery.server.database.manager import Manager


class CommonMapper(object):
    """
    Common data mapper.
    """
    def __init__(self, model_name):
        session_name = settings.WORLD_DATA_MODEL_FILE
        self.session = Manager.instance().get_session(session_name)
        self.model_name = model_name
        module = importlib.import_module(session_name)
        self.model = getattr(module, model_name)

    def all(self):
        query = self.session.query(self.model)
        return query.all()

    def get(self, **kwargs):
        """
        Get a record with conditions in kwargs.
        """
        query = self.session.query(self.model)

        for field, value in kwargs:
            query = query.filter(getattr(self.model, field) == value)

        return query.one()

    def filter(self, **kwargs):
        """
        Get a list of records with conditions in kwargs.
        """
        query = self.session.query(self.model)

        for field, value in kwargs:
            query = query.filter(getattr(self.model, field) == value)

        return query.all()


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
            return q.get_all_from_tables([self.model_name])
        else:
            return q.get_all_from_tables([self.base_model_name, self.model_name])

    def get_by_key_with_base(self, key):
        """
        Get a record with its base data.

        Args:
            key: (string) object's key.
        """
        if self.base_model_name == self.model_name:
            return q.get_tables_record_by_key([self.model_name], key)
        else:
            return q.get_tables_record_by_key([self.base_model_name, self.model_name], key)
