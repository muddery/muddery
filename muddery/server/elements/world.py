"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

from evennia.utils import logger
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.world_areas import WorldAreas
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class MudderyWorld(BaseElement):
    """
    The whole world which contains all areas.
    """
    element_type = "WORLD"
    element_name = _("World", "elements")

    def load_data(self, key, level=None):
        """
        Load the object's data.

        :arg
            key: (string) the key of the data.
            level: (int) element's level.

        :return:
        """
        # Load data.
        self.load_areas()

    def load_areas(self):
        """
        Load all areas.
        """
        records = WorldAreas.all()
        models = ELEMENT("AREA").get_models()
        self.all_areas = {}

        # self.all_rooms {
        #   room's key: area's key
        # }
        self.room_dict = {}
        for record in records:
            tables_data = WorldData.get_tables_data(models, record.key)
            tables_data = tables_data[0]

            new_obj = ELEMENT("AREA")()
            new_obj.setup_element(tables_data.key)

            self.all_areas[new_obj.get_id()] = new_obj

            rooms_key = new_obj.get_rooms_key()
            for key in rooms_key:
                self.room_dict[key] = tables_data.key
