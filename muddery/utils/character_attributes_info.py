"""
Handles characters attributes.
"""

from muddery.utils.localized_strings_handler import _
from django.db.models import Model
from worlddata import models
from muddery.worlddata.model_base import character_attributes
from muddery.worlddata.data_sets import DATA_SETS
from muddery.utils.utils import is_child


class CharacterAttributesInfo(object):
    """
    Handles character attribute's information.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.clear()

    def clear(self):
        """
        Clear data.
        """
        self.fields = {}
        self.keys = {}

    def reload(self):
        """
        Reload local string data.
        """
        self.clear()

        # Load localized string model.
        try:
            for record in DATA_SETS.character_attributes_info.objects.all():
                # Add db fields to dict.
                values = {"field": record.field,
                          "key": record.key,
                          "name": record.name,
                          "desc": record.desc}
                self.fields[record.field] = values
                self.keys[record.field] = values
        except Exception, e:
            print("Can not load character attribute: %s" % e)

        self.set_model_fields()

    def has_field(self, field):
        """
        Check if object has this field.
        """
        return field in self.fields

    def has_key(self, key):
        """
        Check if object has this key.
        """
        return key in self.keys

    def for_field(self, field):
        """
        Get the attribute information for this field.
        """
        return self.fields.get(field, None)

    def for_key(self, key):
        """
        Get the attribute information for this key.
        """
        return self.keys.get(key, None)

    def set_model_fields(self):
        """
        Set model fields names to attribute names.
        """
        for model_name in dir(models):
            # get model classes
            model = getattr(models, model_name)
            if type(model) != type(Model):
                continue

            if not is_child(model, character_attributes):
                continue

            # get model fields
            for field in model._meta.fields:
                print "field: %s" % field
                info = self.keys.get(field.name, None)
                if info:
                    field.verbose_name = info["name"]
                    field.help_text = info["desc"]

    def set_form_fields(self, form):
        """
        Set form fields names to attribute names.
        """
        form_fields = form.fields
        model_fields = form.Meta.model._meta.fields

        for field in model_fields:
            if field.name in form_fields:
                info = self.keys.get(field.name, None)
                if info:
                    form_fields[field.name].label = info["name"]
                    form_fields[field.name].help_text = info["desc"]


# character attribute handler
CHARACTER_ATTRIBUTES_INFO = CharacterAttributesInfo()
