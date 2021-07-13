"""
The World is the base controller of a server. It managers all areas, maps and characters on this server.
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

    def __init__(self, *agrs, **wargs):
        super(MudderyWorld, self).__init__(*agrs, **wargs)

        # All areas in this world.
        # all_areas: {area's key: area's object}
        self.all_areas = {}

        # All rooms in this world.
        # room_dict: {room's key: area's key}
        self.room_dict = {}

        # All characters in this world.
        # all_characters: {character's db id: character's object
        self.all_characters = {}

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
        base_model = ELEMENT("AREA").get_base_model()
        self.all_areas = {}

        # self.room_dict {
        #   room's key: area's key
        # }
        self.room_dict = {}
        for record in records:
            table_data = WorldData.get_table_data(base_model, key=record.key)
            table_data = table_data[0]

            new_area = ELEMENT(table_data.element_type)()
            new_area.setup_element(record.key)

            self.all_areas[new_area.get_element_key()] = new_area

            rooms_key = new_area.get_rooms_key()
            for key in rooms_key:
                self.room_dict[key] = record.key

    def get_room(self, room_key):
        """
        Get a room by its key.
        :param room_key:
        :return:
        """
        area_key = self.room_dict[room_key]
        return self.all_areas[area_key].get_room(room_key)

    def get_area_by_room(self, room_key):
        """
        Get the room's area.
        :param room_key:
        :return:
        """
        area_key = self.room_dict[room_key]
        return self.all_areas[area_key]

    def on_char_puppet(self, character):
        """
        Called when a player puppet a character.

        :param character:
        :return:
        """
        self.all_characters[character.get_db_id()] = character

    def on_char_unpuppet(self, character):
        """
        Called when a player puppet a character.

        :param character:
        :return:
        """
        self.all_characters[character.get_db_id()] = character

    def get_character(self, char_db_id):
        """
        Get a character's object by ist db id.

        :param char_db_id:
        :return:
        """
        return self.all_characters[char_db_id]
