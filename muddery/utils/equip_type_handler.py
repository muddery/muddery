"""
Equipment type handler.
"""

from django.conf import settings
from django.db.models.loading import get_model


class EquipTypeHandler(object):
    """
    The model maintains two tables of equip_type->careers and career->equip_types.
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
        self.equip_career = {}

    
    def reload(self):
        """
        Reload data.
        """
        self.clear()

        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.EQUIP_TYPES)
            for record in model_obj.objects.all():
                self.equip_career[record.type] = set(record.career.split(","))
        except Exception, e:
            pass

    
    def can_equip(self, equip, career):
        """
        Check if can equip.
        """
        if not type in self.equip_career:
            return False

        return career in self.equip_career[equip]


# main dialoguehandler
EQUIP_TYPE_HANDLER = EquipTypeHandler()
