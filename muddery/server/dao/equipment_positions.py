
from muddery.server.dao.worlddata import WorldData


class EquipmentPositions(object):
    """
    Equipment positions data.
    """
    table_name = "equipment_positions"

    @classmethod
    def all(cls):
        return WorldData.get_table_all(cls.table_name)
