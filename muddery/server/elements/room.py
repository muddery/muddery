"""
Room

Rooms are simple containers that has no location of their own.

"""

import ast
import asyncio
import traceback

from muddery.server.utils.logger import logger
from muddery.server.utils.game_settings import GameSettings
from muddery.server.database.worlddata.image_resource import ImageResource
from muddery.server.database.worlddata.world_npcs import WorldNPCs
from muddery.server.database.worlddata.world_exits import WorldExits
from muddery.server.database.worlddata.world_objects import WorldObjects
from muddery.server.mappings.element_set import ELEMENT
from muddery.common.utils.defines import ConversationType, EventType
from muddery.server.utils.localized_strings_handler import _
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.common.utils.utils import async_wait


class MudderyRoom(ELEMENT("MATTER")):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    element_type = "ROOM"
    element_name = "Room"
    model_name = "world_rooms"

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyRoom, self).__init__()

        self.peaceful = False
        self.position = None
        self.background = None

        self.all_exits = {}
        self.all_objects = {}
        self.neighbours = set()
        self.map_data = {}

        # character_list: {
        #   character's id: character's object
        # }
        self.all_characters = {}

    async def at_element_setup(self, first_time):
        """
        Set data_info to the object.
        """
        await super(MudderyRoom, self).at_element_setup(first_time)

        self.all_exits = {}
        self.all_objects = {}

        # character_list: {
        #   character's id: character's object
        # }
        self.all_characters = {}

        self.peaceful = self.const.peaceful

        self.position = None
        try:
            # set position
            position = self.const.position
            if position:
                self.position = ast.literal_eval(position)
        except Exception as e:
            logger.log_trace("load position error: %s" % e)

        # get background
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

        # Load exits, objects and NPCs.
        await async_wait([
            self.load_exits(),
            self.load_objects(),
            self.load_npcs(),
        ])

    def load_map(self):
        """
        Load the room's map data.
        """
        # set neighbours
        self.neighbours = set([item["destination"] for item in self.all_exits.values()])

        # Set map data
        map_data = self.get_appearance()
        if self.position:
            map_data["pos"] = self.position

        map_data["objects"] = [item["obj"].get_appearance() for item in self.all_objects.values()]

        map_data["exits"] = [
            dict(item["obj"].get_appearance(), **{
                "to": item["destination"],
            }) for item in self.all_exits.values()
        ]

        self.map_data = map_data
        return self.map_data

    async def load_npcs(self):
        """
        Load NPCs in this room.

        :return:
        """
        records = WorldNPCs.get_location(self.get_element_key())
        models = ELEMENT("WORLD_NPC").get_models()

        self.all_characters = {}
        awaits = []
        for record in records:
            try:
                tables_data = WorldData.get_tables_data(models, record.key)
                tables_data = tables_data[0]

                new_obj = ELEMENT(tables_data.element_type)()
                self.all_characters[new_obj.get_id()] = new_obj
                awaits.append(new_obj.setup_element(tables_data.key, level=tables_data.level, first_time=True))
            except Exception as e:
                logger.log_trace("Load NPC %s error: %s" % (record.key, e))

        if awaits:
            await async_wait(awaits)

        # Set the character's location.
        for obj in self.all_characters.values():
            obj.set_location(self)

    async def load_exits(self):
        """
        Load exits in this room.

        :return:
        """
        records = WorldExits.get_location(self.get_element_key())
        models = ELEMENT("EXIT").get_models()

        self.all_exits = {}
        for record in records:
            tables_data = WorldData.get_tables_data(models, record.key)
            tables_data = tables_data[0]

            new_obj = ELEMENT(tables_data.element_type)()
            self.all_exits[record.key] = {
                "destination": tables_data.destination,
                "verb": tables_data.verb,
                "obj": new_obj,
            }

        if self.all_exits:
            await async_wait([item["obj"].setup_element(key) for key, item in self.all_exits.items()])

    async def load_objects(self):
        """
        Load objects in this room.

        :return:
        """
        records = WorldObjects.get_location(self.get_element_key())
        models = ELEMENT("WORLD_OBJECT").get_models()

        self.all_objects = {}
        for record in records:
            tables_data = WorldData.get_tables_data(models, record.key)
            tables_data = tables_data[0]

            new_obj = ELEMENT(tables_data.element_type)()

            self.all_objects[record.key] = {
                "obj": new_obj,
            }

        if self.all_objects:
            await async_wait([obj["obj"].setup_element(key) for key, obj in self.all_objects.items()])

    def get_character(self, char_id):
        """
        Get a character in the room.

        :param char_id:
        :return:
        """
        return self.all_characters[char_id]

    def get_object(self, object_key):
        """
        Get an object in the room.

        :param object_key:
        :return:
        """
        return self.all_objects[object_key]["obj"]

    def get_exit(self, exit_key):
        """
        Get an exit in the room.

        :param exit_key:
        :return:
        """
        return self.all_exits[exit_key]["obj"]

    async def can_unlock_exit(self, caller, exit_key):
        """
        Unlock an exit. Add the exit's key to the character's unlock list.
        """
        if exit_key not in self.all_exits:
            return False

        exit_obj = self.all_exits[exit_key]["obj"]
        if not await exit_obj.can_unlock(caller):
            return False

        return True

    async def get_exit_appearance(self, caller, exit_key):
        """
        Get the appearance of an exit.
        :param caller:
        :param exit_key:
        :return:
        """
        exit_obj = self.all_exits[exit_key]["obj"]
        return await exit_obj.get_detail_appearance(caller)

    async def msg_characters(self, msg, exclude=None):
        """
        Send a message to all characters in the room.
        :param msg:
        :param exclude: (set) send the message to characters exclude these characters.
        :return:
        """
        if exclude:
            chars = [char for char_id, char in self.all_characters.items() if char_id not in exclude]
        else:
            chars = self.all_characters.values()

        if chars:
            await async_wait([char.msg(msg) for char in chars])

    async def at_character_arrive(self, character):
        """
        Called after an object has been moved into this object.

        Args:
        character (Object): The character moved into this one

        """
        self.all_characters[character.get_id()] = character

        # send surrounding changes to player
        if not character.is_staff():
            # Players can not see staffs.
            if not GameSettings.inst().get("solo_mode") or not character.is_player():
                # Players can not see other players in solo mode.
                change = {
                    "type": "players" if character.is_player() else "npcs",
                    "id": character.get_id(),
                    "name": character.get_name()
                }
                await self.msg_characters({"obj_moved_in": change}, {character.get_id()})

    async def at_character_leave(self, character):
        """
        Called when a character leave this room.

        :param character: The character leaving.
        :return:
        """
        try:
            del self.all_characters[character.get_id()]
        except KeyError:
            pass

        # send surrounding changes to player
        if not character.is_staff():
            # Players can not see staffs.
            if not GameSettings.inst().get("solo_mode") or not character.is_player():
                # Players can not see other players in solo mode.
                change = {
                    "type": "players" if character.is_player() else "npcs",
                    "id": character.get_id(),
                    "name": character.get_name()
                }
                await self.msg_characters({"obj_moved_out": change}, {character.get_id()})

    def get_appearance(self):
        """
        Get the common appearance of the room. It is the same to all players.
        """
        info = super(MudderyRoom, self).get_appearance()
        info["peaceful"] = self.peaceful
        info["background"] = self.background
        return info

    def get_map_data(self):
        """
        Get the room's map.
        :return:
        """
        return self.map_data

    def get_surroundings(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name, description, commands and all objects in it
        info = {}

        if not GameSettings.inst().get("solo_mode"):
            # Players can not see other players in solo mode.
            players = [{
                "id": item.get_id(),
                "key": key,
                "name": item.get_name(),
                "icon": item.get_icon(),
            } for key, item in self.all_characters.items() if item.is_player() and item.get_id() != caller.get_id()]

            if players:
                info["players"] = players

        npcs = [{
            "id": item.get_id(),
            "key": key,
            "name": item.get_name(),
            "icon": item.get_icon(),
        } for key, item in self.all_characters.items() if not item.is_player()]

        if npcs:
            info["npcs"] = npcs

        return info

    @classmethod
    def get_event_trigger_types(cls):
        """
        Get an object's available event triggers.
        """
        return [EventType.EVENT_TRIGGER_ARRIVE]

    async def get_message(self, caller, message):
        """
        Receive a message from a character.

        :param caller: talker.
        :param message: content.
        """
        output = {
            "type": ConversationType.LOCAL.value,
            "channel": self.get_name(),
            "from_id": caller.get_id(),
            "from_name": caller.get_name(),
            "msg": message
        }

        if GameSettings.inst().get("solo_mode"):
            await caller.msg({"conversation": output})
        else:
            await self.msg_characters({"conversation": output})
