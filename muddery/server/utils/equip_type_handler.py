"""
This handles the relations of equipment types and character careers.
"""


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

        """
        try:
            for record in CM.CAREER_EQUIPMENTS.all():
                career = record.serializable_value("career")
                equipment = record.serializable_value("equipment")
                if career not in self.career_equip:
                    self.career_equip[career] = set()
                self.career_equip[career].add(equipment)
        except Exception as e:
            logger.log_errmsg("Can not load career equipment types: %s" % e)
            pass
        """
    
    def can_equip(self, career, equip):
        """
        Check if the equipment's type matchs career.
        """
        if not self.career_equip:
            return True
        if career not in self.career_equip:
            return False
        if not self.career_equip[career]:
            return False
        return equip in self.career_equip[career]


# main handler
EQUIP_TYPE_HANDLER = EquipTypeHandler()
