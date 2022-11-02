"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

from muddery.common.utils.utils import async_wait
from muddery.server.utils.logger import logger
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.worlddata.image_resource import ImageResource
from muddery.server.database.worlddata.world_rooms import WorldRooms
from muddery.server.database.worlddata.worlddata import WorldData


class MudderyArea(ELEMENT("MATTER")):
    """
    Areas are compose the whole map. Rooms are belongs to areas.
    """
    element_type = "AREA"
    element_name = "Area"
    model_name = "world_areas"

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyArea, self).__init__()

        self.background = None
        self.all_rooms = {}
        self.map_data = {}

    async def at_element_setup(self, first_time):
        """
        Init the character.
        """
        await super(MudderyArea, self).at_element_setup(first_time)

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
                logger.log_trace("Load background %s error: %s" % (resource, e))

        # load rooms in this area
        await self.load_rooms()

    def get_appearance(self):
        """
        The common appearance for all players.
        """
        info = super(MudderyArea, self).get_appearance()
        info["background"] = self.background
        return info

    def load_map(self):
        """
        Load the area's map data.
        """
        map_data = self.get_appearance()
        map_data["rooms"] = {
            key: room.load_map() for key, room in self.all_rooms.items()
        }
        self.map_data = map_data
        return self.map_data

    def get_map_data(self):
        """
        Get the area's map data.
        :return:
        {
            area's appearance,
            "rooms" : {
                room's key: {
                    room's appearance,
                    "exits": {
                        {
                            exit's key:
                                {
                                    exit's appearance,
                                    "from": room's key,
                                    "to": room's key,
                                },
                        }
                },
            }
        }
        """
        return self.map_data

    async def load_rooms(self):
        """
        Load all rooms in this area.

        :return:
        """
        records = WorldRooms.get_by_area(self.get_element_key())
        base_model = ELEMENT("ROOM").get_base_model()

        self.all_rooms = {}
        for record in records:
            table_data = WorldData.get_table_data(base_model, key=record.key)
            table_data = table_data[0]

            new_obj = ELEMENT(table_data.element_type)()
            self.all_rooms[record.key] = new_obj

        if self.all_rooms:
            await async_wait([obj.setup_element(key) for key, obj in self.all_rooms.items()])

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
