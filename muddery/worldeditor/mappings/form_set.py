"""
This model translates default strings into localized strings.
"""

from django.conf import settings
from django.contrib.admin.forms import forms
from muddery.server.utils import logger
from muddery.server.utils.utils import classes_in_path


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
        for cls in classes_in_path(settings.PATH_DATA_FORMS_BASE, forms.ModelForm):
            if hasattr(cls, "Meta") and hasattr(cls.Meta, "model"):
                model = cls.Meta.model
                model_name = model.__name__

                if model_name in self.dict:
                    logger.log_info("Form %s is replaced by %s." % (model_name, cls))

                self.dict[model_name] = cls

    def get(self, model_name):
        """
        Get a form.

        Args:
            model_name: (string) model's name
        """
        return self.dict[model_name]


FORM_SET = FormSet()

