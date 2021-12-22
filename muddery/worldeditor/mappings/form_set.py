"""
This model translates default strings into localized strings.
"""

import importlib, inspect
from django.conf import settings
from django import forms
from muddery.server.utils.logger import logger
from muddery.worldeditor.forms.create_form import Form


class FormSet(object):
    """
    All available elements.
    """
    def __init__(self):
        self.dict = {}
        self.load()
        
    def load(self):
        """
        Add all forms from the form path.
        """
        # load classes
        base_class = Form
        module = importlib.import_module(settings.PATH_DATA_FORMS_BASE)
        for name, obj in vars(module).items():
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not base_class:
                cls = obj
                if hasattr(cls, "Info"):
                    info = cls.Info
                    table_name = info.table_name

                    if table_name in self.dict:
                        logger.log_info("Form %s is replaced by %s." % (table_name, cls))

                    self.dict[table_name] = cls

    def get(self, table_name):
        """
        Get a form.

        Args:
            table_name: (string) table's name
        """
        return self.dict[table_name]


FORM_SET = FormSet()

