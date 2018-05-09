"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from worlddata import forms


class FormsMapper:
    def __init__(self):
        self.dict = {}

        for name in dir(forms):
            try:
                form_class = getattr(forms, name)
                model_name = form_class.Meta.model.__name__
                self.dict[model_name] = form_class
            except Exception, e:
                pass

    def get_form(self, model_name):
        """
        Get form class by model's name.

        Args:
            model_name: model's name

        Returns:
            form's class
        """
        return self.dict[model_name]

FORMS_MAPPER = FormsMapper()

