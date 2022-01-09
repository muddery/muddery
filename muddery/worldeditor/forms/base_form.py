
"""
The base of all forms.
"""
from django.conf import settings
from wtforms import fields
from wtforms_alchemy import ModelForm
from muddery.worldeditor.database.db_manager import DBManager
from muddery.server.utils.localized_strings_handler import _


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
    def get_session(cls):
        # this method should return sqlalchemy session
        return DBManager.inst().get_session(settings.WORLD_DATA_APP)

    # add id field manually
    id = fields.HiddenField(id="id", name="id", description="id")
