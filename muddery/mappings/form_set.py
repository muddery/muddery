"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from django.conf import settings
from django.contrib.admin.forms import forms
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.utils.utils import classes_in_path


class FormSet(object):
    """
    All available typeclasses.
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

                if self.dict.has_key(model_name):
                    logger.log_infomsg("Form %s is replaced by %s." % (model_name, cls))

                self.dict[model_name] = cls

    def get(self, model_name):
        """
        Get a form.

        Args:
            model_name: (string) model's name
        """
        return self.dict[model_name]


FORM_SET = FormSet()

