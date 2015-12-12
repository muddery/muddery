"""
This handles the relations of equipment types and character careers.
"""

from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class EquipTypeHandler(object):
    """
    The model maintains a dict of equip_type to careers.
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
            model_obj = get_model(settings.WORLD_DATA_APP, settings.EQUIPMENT_TYPES)
            for record in model_obj.objects.all():
                self.equip_career[record.type] = set(record.career.split(","))
        except Exception, e:
            logger.log_errmsg("Can not load equipment types: %s" % e)
            pass

    
    def can_equip(self, equip, career):
        """
        Check if the equipment's type matchs career.
        """
        if not equip in self.equip_career:
            return False

        if not self.equip_career[equip]:
            return True

        return career in self.equip_career[equip]


# main dialoguehandler
EQUIP_TYPE_HANDLER = EquipTypeHandler()
