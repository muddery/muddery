"""
This handles the relations of equipment types and character careers.
"""

from django.conf import settings
from django.apps import apps
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
        self.career_equip = {}

    
    def reload(self):
        """
        Reload data.
        """
        self.clear()

        try:
            model_obj = apps.get_model(settings.WORLD_DATA_APP, settings.CAREER_EQUIPMENTS)
            for record in model_obj.objects.all():
                career = record.serializable_value("career")
                equipment = record.serializable_value("equipment")
                if career not in self.career_equip:
                    self.career_equip[career] = set()
                self.career_equip[career].add(equipment)
        except Exception, e:
            logger.log_errmsg("Can not load career equipment types: %s" % e)
            pass

    
    def can_equip(self, career, equip):
        """
        Check if the equipment's type matchs career.
        """
        if career not in self.career_equip:
            return False
        if not self.career_equip[career]:
            return False
        return equip in self.career_equip[career]


# main dialoguehandler
EQUIP_TYPE_HANDLER = EquipTypeHandler()
