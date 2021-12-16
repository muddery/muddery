
"""
World data forms.
"""

from wtforms import Form
from django.conf import settings
from muddery.server.database.manager import Manager
from muddery.worldeditor.dao.general_query_mapper import get_all_fields


def get_form(table_name):
    """
    Get a form of a table.
    """
    session = Manager.inst().get_session(settings.WORLD_DATA_APP)
    model = Manager.inst().get_model(session, table_name)
    fields = get_all_fields(table_name)

    cls = Form
    return cls()
