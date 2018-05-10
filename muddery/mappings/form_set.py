"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.worlddata import forms


def form_mapping(form):
    """
    A decorator which add a form to the public form set.
    """
    FORM_SET.add(form)
    return form


class FormSet(object):
    """
    All available typeclasses.
    """
    def __init__(self):
        self.dict = {}
        
    def add(self, form):
        """
        Add a form.

        Args:
            form: (class) form's class.
        """
        if not form:
            raise MudderyError("Missing form.")

        model_name = form.Meta.model.__name__

        if self.dict.has_key(model_name):
            logger.log_infomsg("Form %s is replaced with %s.", (model_name, form))

        self.dict[model_name] = form

    def get(self, model_name):
        """
        Get a form.

        Args:
            model_name: (string) model's name
        """
        return self.dict[model_name]


FORM_SET = FormSet()
