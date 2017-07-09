"""
Handles characters attributes.
"""

from muddery.utils.localized_strings_handler import _
from muddery.worlddata.data_sets import DATA_SETS


class AttributesInfoHandler(object):
    """
    Handles character attribute's information.
    """
    def __init__(self, model_data_handler, info_data_handler):
        """
        Initialize handler
        """
        self.model_data_handler = model_data_handler
        self.info_data_handler = info_data_handler
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
            for record in self.info_data_handler.objects.all():
                if not record.key:
                    # skip empty fields
                    continue

                # Add db fields to dict.
                values = {"field": record.field,
                          "key": record.key,
                          "name": record.name,
                          "desc": record.desc}
                self.fields[record.field] = values
                self.keys[record.key] = values
        except Exception, e:
            print("Can not load attribute: %s" % e)

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

    def all_keys(self):
        """
        Get all keys.
        """
        return self.keys.keys()

    def all_values(self):
        """
        Get all values.
        """
        return self.keys.values()

    def set_model_fields(self):
        """
        Set model fields names to attribute names.
        """
        model = self.model_data_handler.model

        # get model fields
        for field in model._meta.fields:
            info = self.fields.get(field.name, None)
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
CHARACTER_ATTRIBUTES_INFO = AttributesInfoHandler(DATA_SETS.character_models, DATA_SETS.character_attributes_info)
EQUIPMENT_ATTRIBUTES_INFO = AttributesInfoHandler(DATA_SETS.equipments, DATA_SETS.equipment_attributes_info)
FOOD_ATTRIBUTES_INFO = AttributesInfoHandler(DATA_SETS.foods, DATA_SETS.food_attributes_info)
