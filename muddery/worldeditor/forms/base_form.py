
"""
The base of all forms.
"""
from wtforms import fields
from wtforms_alchemy import ModelForm
from muddery.server.database.worlddata_db import WorldDataDB
from muddery.worldeditor.settings import SETTINGS


class FormData(object):
    """
    Make a dict looks like a request form.
    """

    def __init__(self, data):
        """
        Args:
            data: (dict) a dict of data.
        """
        self.data = data

    def __contains__(self, item):
        return item in self.data

    def getlist(self, key):
        """
        Get a value by the key.
        """
        return [self.data[key]]


class BaseForm(ModelForm):
    """
    The base of all forms.
    """
    @classmethod
    def refresh(cls):
        pass

    @classmethod
    def get_session(cls):
        # this method should return sqlalchemy session
        return WorldDataDB.inst().get_session()

    # add id field manually
    id = fields.HiddenField(id="id", name="id", description="id")
