"""
This model localize other models.
"""

from muddery.utils.localized_strings_handler import _
from django.db.models import Model
from worlddata import models


def localize_model_fields():
    """
    Localize models field's verbose name and help text.
    """
    for model_name in dir(models):
        # get model classes
        model = getattr(models, model_name)
        if type(model) != type(Model):
            continue

        # get model fields
        for field in model._meta.fields:
            field.verbose_name = _(field.name, "field_" + model.__name__)
            field.help_text = _(field.name, "help_" + model.__name__, "")


def localize_form_field(form, field_name):
    """
    Localize form field's label and help text.
    """
    form_fields = form.fields
    model_fields = form.Meta.model._meta.fields

    for field in model_fields:
        if field.name == field_name:
            if field_name in form_fields:
                form_fields[field_name].label = field.verbose_name
                form_fields[field_name].help_text = field.help_text


def localize_form_fields(form):
    """
    Localize form field's label and help text.
    """
    form_fields = form.fields
    model_fields = form.Meta.model._meta.fields

    for field in model_fields:
        if field.name in form_fields:
            form_fields[field.name].label = field.verbose_name
            form_fields[field.name].help_text = field.help_text
