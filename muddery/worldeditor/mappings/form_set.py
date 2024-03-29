"""
This model translates default strings into localized strings.
"""

import importlib, inspect
from wtforms_alchemy import ModelForm
from sqlalchemy.ext.declarative import declarative_base
from muddery.worldeditor.utils.logger import logger
from muddery.worldeditor.settings import SETTINGS
Base = declarative_base()


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
        base_class = ModelForm
        module = importlib.import_module(SETTINGS.PATH_DATA_FORMS_BASE)
        for name, obj in vars(module).items():
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not base_class:
                form_class = obj
                if form_class.Meta and form_class.Meta.model:
                    model_name = form_class.Meta.model.__name__
                    if model_name and model_name in self.dict:
                        logger.log_debug("Form %s is replaced by %s." % (model_name, form_class))

                    self.dict[model_name] = form_class

    def get(self, table_name):
        """
        Get a form.

        Args:
            table_name: (string) table's name
        """
        form = self.dict[table_name]
        form.refresh()
        return form


FORM_SET = FormSet()

