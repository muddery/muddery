"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

from evennia.utils import logger
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _
from muddery.server.database.worlddata.image_resource import ImageResource
from muddery.server.database.worlddata.world_rooms import WorldRooms
from muddery.server.database.worlddata.worlddata import WorldData


class MudderyArea(BaseElement):
    """
    Areas are compose the whole map. Rooms are belongs to areas.
    """
    element_type = "AREA"
    element_name = _("Area", "elements")
    model_name = "world_areas"

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyArea, self).__init__()

        self.name = None
        self.desc = None
        self.icon = None
        self.background = None
        self.all_rooms = {}

    def at_element_setup(self, first_time):
        """
        Init the character.
        """
        super(MudderyArea, self).at_element_setup(first_time)

        self.set_name(self.const.name)
        self.set_desc(self.const.desc)
        self.set_icon(self.const.icon)

        self.background = None
        resource = self.const.background
        if resource:
            try:
                resource_info = ImageResource.get(resource)
                resource_info = resource_info[0]
                self.background = {"resource": resource_info.resource,
                                   "width": resource_info.image_width,
                                   "height": resource_info.image_height}
            except Exception as e:
                logger.log_tracemsg("Load background %s error: %s" % (resource, e))

        # load rooms in this area
        self.load_rooms()

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = {
            "key": self.get_element_key(),
            "name": self.get_name(),
            "desc": self.get_desc(),
            "icon": self.get_icon(),
            "background": self.background,
        }
        
        return info

    def set_name(self, name):
        """
        Set object's name.

        Args:
        name: (string) Name of the object.
        """
        self.name = name

    def get_name(self):
        """
        Get player character's name.
        """
        return self.name

    def set_desc(self, desc):
        """
        Set object's description.

        Args:
        desc: (string) Description.
        """
        self.desc = desc

    def get_desc(self):
        """
        Get the element's description.
        :return:
        """
        return self.desc

    def set_icon(self, icon_key):
        """
        Set object's icon.
        Args:
            icon_key: (String)icon's resource key.

        Returns:
            None
        """
        self.icon = icon_key

    def get_icon(self):
        """
        Get object's icon.
        :return:
        """
        return self.icon

    def load_rooms(self):
        """
        Load all rooms in this area.

        :return:
        """
        records = WorldRooms.get_by_area(self.get_element_key())
        models = ELEMENT("ROOM").get_models()
        self.all_rooms = {}
        for record in records:
            tables_data = WorldData.get_tables_data(models, record.key)
            tables_data = tables_data[0]

            new_obj = ELEMENT("ROOM")()
            new_obj.setup_element(tables_data.key)

            self.all_rooms[new_obj.get_element_key()] = new_obj

    def get_rooms_key(self):
        """
        Get keys of all rooms in this area.
        :return:
        """
        return self.all_rooms.keys()

    def get_room(self, room_key):
        """
        Get a room by its key.
        :param room_key:
        :return:
        """
        return self.all_rooms[room_key]
