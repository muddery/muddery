"""
The World is the base controller of a server. It managers all areas, maps and characters on this server.
"""

from muddery.server.conf import settings
from muddery.server.elements.base_element import BaseElement
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.gamedata.honours_mapper import HonoursMapper
from muddery.server.database.worlddata.world_areas import WorldAreas
from muddery.server.database.worlddata.world_channels import WorldChannels
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.defines import ConversationType
from muddery.server.utils.utils import class_from_path


class MudderyWorld(BaseElement):
    """
    The whole world which contains all areas.
    """
    element_type = "WORLD"
    element_name = "World"

    def __init__(self, *agrs, **wargs):
        super(MudderyWorld, self).__init__(*agrs, **wargs)

        # All channels in this world.
        # all_channels: {channel's key: channel's object}
        self.all_channels = {}

        # All areas in this world.
        # all_areas: {area's key: area's object}
        self.all_areas = {}

        # All rooms in this world.
        # room_dict: {room's key: area's key}
        self.room_dict = {}

        # All characters in this world.
        # all_characters: {character's db id: character's object
        self.all_characters = {}

    async def load_data(self, key, level=None):
        """
        Load the object's data.

        :arg
            key: (string) the key of the data.
            level: (int) element's level.

        :return:
        """
        # Load data.
        await HonoursMapper.inst().init()
        await self.load_channels()
        await self.load_areas()
        self.load_commands()

    async def load_channels(self):
        """
        Load all channels.
        """
        records = WorldChannels.all()
        base_model = ELEMENT("CHANNEL").get_base_model()
        self.all_channels = {}

        for record in records:
            table_data = WorldData.get_table_data(base_model, key=record.key)
            table_data = table_data[0]

            new_channel = ELEMENT(table_data.element_type)()
            await new_channel.setup_element(record.key)

            self.all_channels[new_channel.get_element_key()] = new_channel

    async def load_areas(self):
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
            await new_area.setup_element(record.key)

            self.all_areas[new_area.get_element_key()] = new_area

            rooms_key = new_area.get_rooms_key()
            for key in rooms_key:
                self.room_dict[key] = record.key

    def load_commands(self):
        """
        Load all client commands.
        """
        session_cmdset = class_from_path(settings.SESSION_CMDSET)
        session_cmdset.create()

        account_cmdset = class_from_path(settings.ACCOUNT_CMDSET)
        account_cmdset.create()

        character_cmdset = class_from_path(settings.CHARACTER_CMDSET)
        character_cmdset.create()

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
        char_db_id = character.get_db_id()
        self.all_characters[char_db_id] = character

        for channel in self.all_channels.values():
            channel.add_character(char_db_id)

    def on_char_unpuppet(self, character):
        """
        Called when a player puppet a character.

        :param character:
        :return:
        """
        char_db_id = character.get_db_id()
        del self.all_characters[char_db_id]

        for channel in self.all_channels.values():
            channel.remove_character(char_db_id)

    def get_character(self, char_db_id):
        """
        Get a character's object by ist db id.

        :param char_db_id:
        :return:
        """
        return self.all_characters[char_db_id]

    def get_all_channels(self):
        """
        Get a channel by its key.
        """
        return self.all_channels

    def get_channel(self, channel_key):
        """
        Get a channel by its key.
        """
        return self.all_channels[channel_key]

    async def send_message(self, caller, target_type, target, message):
        """
        Send a player's message to the target.
        """
        if target_type == ConversationType.CHANNEL.value:
            channel = self.get_channel(target)
            channel.get_message(caller, message)
        elif target_type == ConversationType.LOCAL.value:
            room = self.get_room(target)
            await room.get_message(caller, message)
        elif target_type == ConversationType.PRIVATE.value:
            character = self.get_character(int(target))
            await character.get_message(caller, message)

    def broadcast(self, message):
        """
        Broadcast a message to all clients.
        """
        # TODO
        pass
