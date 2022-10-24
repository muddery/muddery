"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import weakref
from muddery.server.utils.logger import logger
from muddery.server.server import Server
from muddery.server.utils.quest_handler import QuestHandler
from muddery.server.utils.statement_attribute_handler import StatementAttributeHandler
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GameSettings
from muddery.server.utils.dialogue_handler import DialogueHandler
from muddery.common.utils.defines import ConversationType
from muddery.common.utils.defines import CombatType
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.default_skills import DefaultSkills
from muddery.server.database.worlddata.honour_settings import HonourSettings
from muddery.server.database.worlddata.default_objects import DefaultObjects
from muddery.server.database.worlddata.equipment_positions import EquipmentPositions
from muddery.server.database.worlddata.character_states_dict import CharacterStatesDict
from muddery.server.database.worlddata.characters import Characters
from muddery.server.database.gamedata.character_relationships import CharacterRelationships
from muddery.server.database.gamedata.character_closed_events import CharacterClosedEvents
from muddery.server.mappings.element_set import ELEMENT
from muddery.common.utils import defines
from muddery.server.utils.data_field_handler import DataFieldHandler, ConstDataHolder
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.database.gamedata.honours_mapper import HonoursMapper
from muddery.server.database.gamedata.character_inventory import CharacterInventory
from muddery.server.database.gamedata.character_equipments import CharacterEquipments
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.database.gamedata.character_skills import CharacterSkills
from muddery.server.database.gamedata.character_combat import CharacterCombat
from muddery.server.database.gamedata.character_location import CharacterLocation
from muddery.server.combat.match_pvp import MatchPVPHandler
from muddery.server.utils.object_states_handler import ObjectStatesHandler
from muddery.server.database.gamedata.object_storage import CharacterObjectStorage
from muddery.server.events.event_trigger import EventTrigger
from muddery.common.utils.utils import async_wait, async_gather


class MudderyPlayerCharacter(ELEMENT("CHARACTER")):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    element_type = "PLAYER_CHARACTER"
    element_name = "Player Character"
    model_name = "player_characters"

    def __init__(self):
        """
        Initial the object.
        """
        super(MudderyPlayerCharacter, self).__init__()

        self.pk = 0

        self.states = None
        self.body_data_handler = DataFieldHandler(self)

        self.account = None
        self.account_id = None

        self.name = ""

        # character's inventory
        # inventory: {
        #     position: {
        #         "position": position in the inventory,
        #         "object_key": object's key,
        #         "number": object's number,
        #         "level": object's level,
        #         "obj": object's instance,
        #     }
        # }
        self.inventory = {}

        # character's equipments
        # equipments: {
        #    equipment position: {
        #        "object_key": object's key,
        #        "level": object's level,
        #        "obj": object's instance,
        #    }
        self.equipments = {}

        self.quest_handler = None

        # attributes used in statements
        self.statement_attr = None

        self.event = None

        self.solo_mode = None
        self.current_dialogues = set()

        self.combat_id = None

    def __str__(self):
        """
        Output self as a string
        """
        return "%s(%s)" % (self.name, self.get_db_id())

    # @property body stores character's body properties before using equipments and skills.
    def __body_get(self):
        """
        A non-attr_obj store (ndb: NonDataBase). Everything stored
        to this is guaranteed to be cleared when a server is shutdown.
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.ndb.attr = value etc.
        """
        try:
            return self._body_holder
        except AttributeError:
            # create body handler
            self._body_holder = ConstDataHolder(self, "body_properties", manager_name='body_data_handler')
            return self._body_holder

    # @body.setter
    def __body_set(self, value):
        "Stop accidentally replacing the ndb object"
        string = "Cannot assign directly to ndb object! "
        string += "Use self.body.name=value instead."
        raise Exception(string)

    # @body.deleter
    def __body_del(self):
        "Stop accidental deletion."
        raise Exception("Cannot delete the body object!")
    body = property(__body_get, __body_set, __body_del)

    def create_states_handler(self):
        """
        Characters use memory to store state by default.
        :return:
        """
        return ObjectStatesHandler(self.get_db_id(), CharacterObjectStorage)

    def set_db_id(self, db_id):
        """
        Set the id of the character's data in db.
        :param db_id:
        :return:
        """
        self.db_id = db_id

    def get_db_id(self):
        """
        Get the id of the character's data in db.

        :return:
        """
        return self.db_id

    def is_player(self):
        """
        Check if this is a player character.

        :return:
        """
        return True

    async def set_level(self, level):
        """
        Set element's level.
        :param level:
        :return:
        """
        if self.level == level:
            return

        await CharacterInfo.inst().set_level(self.get_db_id(), level)
        await super(MudderyPlayerCharacter, self).set_level(level)

    async def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        with CharacterInfo.inst().transaction():
            new_level = await self.get_level() + 1
            await self.set_level(new_level)

        return new_level

    async def setup_element(self, key, level=None, first_time=False, temp=False):
        """
        Set element data's key.

        Args:
            key: (string) the key of the data.
            level: (int) element's level.
        """
        if level is None:
            level = await CharacterInfo.inst().get_level(self.get_db_id())

        await super(MudderyPlayerCharacter, self).setup_element(key, level, first_time)

    async def at_element_setup(self, first_time):
        """
        Called when the element is setting up.

        :arg
            first_time: (bool) the first time to setup the element.
        """
        await super(MudderyPlayerCharacter, self).at_element_setup(first_time)

        self.name = await CharacterInfo.inst().get_nickname(self.get_db_id())

        # attributes used in statements
        self.statement_attr = StatementAttributeHandler(self)

        # initialize quests
        self.quest_handler = QuestHandler(self)

        await async_wait([
            self.quest_handler.init(),

            # load inventory
            self.load_inventory(),

            # load equipments
            self.load_equipments(),
        ])

        # initialize events
        self.event = EventTrigger(self)

        self.solo_mode = GameSettings.inst().get("solo_mode")
        self.current_dialogues = set()

    async def after_element_setup(self, first_time):
        """
        Called after the element is setting up.

        :arg
            first_time: (bool) the first time to setup the element.
        """
        await super(MudderyPlayerCharacter, self).after_element_setup(first_time)

        # if it is dead, reborn at init.
        if not self.is_alive:
            if not self.is_temp and self.reborn_time > 0:
                await self.reborn()

        # load combat id
        self.combat_id = await CharacterCombat.inst().load(self.get_db_id(), None)

    async def load_custom_level_data(self, element_type, element_key, level):
        """
        Load body properties from db.
        """
        # Get object level.
        await super(MudderyPlayerCharacter, self).load_custom_level_data(element_type, element_key, level)

        # Set body values.
        for key, info in self.get_properties_info().items():
            value = self.const_data_handler.get(key)
            self.body_data_handler.add(key, value)

    def set_account(self, account):
        """
        Set the player's account.
        :param account:
        :return:
        """
        self.account = weakref.proxy(account)
        self.account_id = account.get_id()

    def get_account_id(self):
        """
        Get the player's account id.
        :return:
        """
        return self.account_id

    async def move_to(self, location):
        """
        Set the character's location(room).
        :param location: location's object
        :return:
        """
        if self.location:
            # Trigger the moving out event.
            self.event.at_character_move_out(self.location)

        # save new location
        location_key = location.get_element_key() if location else ""
        await CharacterLocation.inst().save(self.get_db_id(), location_key)

        if self.location:
            await self.location.at_character_leave(self)

        self.set_location(location)

        results = {}
        if self.location:
            await self.location.at_character_arrive(self)

            # Trigger the arrive event.
            quests, events = await async_gather([
                self.quest_handler.at_objective(defines.OBJECTIVE_ARRIVE, location_key),
                self.event.at_character_move_in(self.location)
            ])
            if quests:
                results["quests"] = quests
            if events:
                results["events"] = events

        return results

    async def at_pre_unpuppet(self):
        """
        Called just before beginning to un-connect a puppeting from
        this Player.
        """
        # Pause all scripts.
        #scripts = self.scripts.all()
        #for script in scripts:
        #    script.pause()

        if not self.solo_mode:
            # notify its location
            if self.location:
                await self.location.at_character_leave(self)

        await MatchPVPHandler.inst().remove(self)

    async def refresh_states(self, keep_states):
        """
        Refresh character's states.

        Args:
            keep_states (boolean): states values keep last values.
        """
         # Load body properties.
        for key, value in self.body_data_handler.all().items():
            self.const_data_handler.add(key, value)

        if not keep_states:
            await super(MudderyPlayerCharacter, self).refresh_states(False)

        # load equips
        await self.wear_equipments()

        # load passive skills
        await self.cast_passive_skills()

        await super(MudderyPlayerCharacter, self).refresh_states(keep_states)

    async def msg(self, data):
        """
        Emits something to the account attached to the object.

        Args:
            data (dict): The message to send
        """
        if not self.account:
            return

        # relay to account
        await self.account.msg(data)

    async def get_level(self):
        """
        Get the character's level.
        :return:
        """
        return await CharacterInfo.inst().get_level(self.get_db_id())

    async def set_nickname(self, nickname):
        """
        Set player character's nickname.
        """
        self.name = nickname
        await CharacterInfo.inst().set_nickname(self.get_db_id(), nickname)

    async def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive:
            commands.append({"name": _("Attack"), "cmd": "attack", "args": self.get_id()})
        return commands

    def get_available_channels(self):
        """
        Get available channel's info.

        Returns:
            (dict) channels
        """
        all_channels = Server.world.get_all_channels()
        channels = {c.get_element_key(): {
            "type": "CHANNEL",
            "name": c.get_name()} for c in all_channels}

        return channels

    def get_maps(self, room_list):
        """
        Get the map of the room's area.
        """
        areas = set([Server.world.get_area_key_by_room(room_key) for room_key in room_list])
        maps = {area_key: Server.world.get_area(area_key).get_map() for area_key in areas if area_key}
        return maps

    def get_neighbour_maps(self, room_key):
        """
        Get the map of the room's neighbour.
        """
        room = Server.world.get_room(room_key)
        exits = room.get_exits()
        neighbours = [exit["to"] for exit in exits.values()]
        return self.get_maps(neighbours)

    async def wear_equipments(self):
        """
        Add equipment's attributes to the character
        """
        # add equipment's attributes
        if self.equipments:
            await async_wait([item["obj"].equip_to(self) for item in self.equipments.values()])

    def get_location_info(self):
        """
        Show characters and objects in this location.
        """
        if not self.location:
            return

        room_key = self.location.get_element_key()
        return {
            "area": Server.world.get_area_key_by_room(room_key),
            "room": room_key,
        }

    def look_around(self):
        """
        Show characters and objects in this location.
        """
        if not self.location:
            return

        return self.location.get_surroundings(self)

    async def get_quests(self):
        """
        Get player's quests info.
        """
        return await self.quest_handler.get_quests()

    ################################################
    #
    # INVENTORY
    #   load_inventory: Load character's inventory from db and check default objects.
    #   total_object_number: get the object's number by key.
    #   has_object: Check the specified object in the inventory.
    #
    ################################################
    async def load_inventory(self):
        """
        Load character's inventory from db and check default objects.

        inventory: {
            position: {
                "position": position in the inventory,
                "object_key": object's key,
                "number": object's number,
                "level": object's level,
                "obj": object's instance,
            }
        }
        """
        inventory = await CharacterInventory.inst().get_character(self.get_db_id())
        self.inventory = {pos: {"position": pos, **inventory[pos]} for pos in sorted(inventory)}

        # load object's data
        common_models = ELEMENT("POCKET_OBJECT").get_models()
        for item in self.inventory.values():
            object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
            object_record = object_record[0]
            item.update({
                "element_type": object_record.element_type,
                "can_remove": object_record.can_remove,
            })

        # default objects
        object_records = DefaultObjects.get(self.get_element_key())

        # add new default objects
        obj_list = []
        for object_record in object_records:
            found = False
            for item in self.inventory.values():
                if object_record.object == item["object_key"]:
                    found = True
                    break
            if not found:
                obj_list.append({
                    "object_key": object_record.object,
                    "level": object_record.level,
                    "number": object_record.number,
                })

        if obj_list:
            await self.receive_objects(obj_list)

    def total_object_number(self, obj_key):
        """
        Get the object's number by key.
        """
        objects = [item["number"] for item in self.inventory.values() if item["object_key"] == obj_key]
        total = sum(objects)
        for item in self.equipments.values():
            if item["object_key"] == obj_key:
                total += 1

        return total

    def has_object(self, obj_key):
        """
        Check the specified object in the inventory.
        """
        return self.total_object_number(obj_key) > 0

    async def receive_object(self, object_key, number, level):
        """
        Add an object to the inventory.
        :param object_key:
        :param number:
        :param level:
        :param mute:
        :return:
        """
        obj_list = [{
            "object_key": object_key,
            "number": number,
            "level": level
        }]
        return await self.receive_objects(obj_list)

    async def receive_objects(self, obj_list):
        """
        Add a list of objects to the inventory.

        Args:
            obj_list: (list) a list of object keys and there numbers.
                             list item: {"object_key": object's key
                                         "number": object's number}
            mute: (boolean) do not send messages to the owner
            show: (boolean) show inventory

        Returns:
            (list) a list of objects that not have been received and their reasons.
            [{
                "key": key,
                "name": name,
                "level": level,
                "number": number,
                "icon": icon,
                "reject": reason,
            }]
        """
        async def add_new_object(object_key, level, number, element_type, can_remove):
            """
            Add a new content to the inventory
            """
            if len(self.inventory) > 0:
                new_position = sorted(self.inventory)[-1] + 1
            else:
                new_position = 1

            self.inventory[new_position] = {
                "position": new_position,
                "object_key": object_key,
                "level": level,
                "number": number,
                "element_type": element_type,
                "can_remove": can_remove,
            }
            await CharacterInventory.inst().add(self.get_db_id(), new_position, object_key, number, level)

        common_models = ELEMENT("POCKET_OBJECT").get_models()

        objects = []           # objects that have been accepted
        for obj in obj_list:
            object_key = obj["object_key"]
            level = obj.get("level", None)
            available = obj["number"]
            number = available
            accepted = 0
            reject = False

            try:
                object_record = WorldData.get_tables_data(common_models, key=object_key)
                object_record = object_record[0]
            except Exception as e:
                logger.log_err("Can not find object %s: %s" % (object_key, e))
                continue

            inventory_obj_list = [pos for pos, item in self.inventory.items() if item["object_key"] == object_key]

            if number == 0:
                # it is an empty object
                if len(inventory_obj_list) > 0:
                    # already has this object
                    continue

                if object_record.can_remove:
                    # remove this empty object
                    continue

                # add a new object to the inventory
                await add_new_object(object_key, level, number, object_record.element_type, object_record.can_remove)

            else:
                # common number
                if object_record.unique:
                    # unique object
                    # Check equipments.
                    in_equipments = False
                    for item in self.equipments.values():
                        if item["object_key"] == object_key:
                            in_equipments = True
                            reject = _("Can not get more %s.") % object_record.name
                            break

                    if not in_equipments:
                        if len(inventory_obj_list) > 0:
                            item = self.inventory[inventory_obj_list[0]]
                            # add object number
                            current_number = item["number"]
                            add = number
                            if add > object_record.max_stack - current_number:
                                add = object_record.max_stack - current_number

                            if add > 0:
                                # increase stack number
                                item["number"] = current_number + add
                                await CharacterInventory.inst().set_dict(self.get_db_id(), item["position"], {"number": current_number + add})
                                number -= add
                                accepted += add
                            else:
                                reject = _("Can not get more %s.") % object_record.name
                        else:
                            # Get the number that actually added.
                            add = number
                            if add > object_record.max_stack:
                                add = object_record.max_stack

                            # add a new object to the inventory
                            await add_new_object(object_key, level, add, object_record.element_type, object_record.can_remove)

                            number -= add
                            accepted += add
                else:
                    # not unique object
                    # if already has this kind of object
                    for index in inventory_obj_list:
                        add = number
                        item = self.inventory[index]
                        current_number = item["number"]

                        if add > object_record.max_stack - current_number:
                            add = object_record.max_stack - current_number

                        if add > 0:
                            # increase stack number
                            item["number"] = current_number + add
                            await CharacterInventory.inst().set_dict(self.get_db_id(), item["position"], {"number": current_number + add})

                            number -= add
                            accepted += add

                        if number == 0:
                            break

                    # if does not have this kind of object, or stack is full
                    while number > 0:
                        if object_record.unique:
                            # can not have more than one unique objects
                            reject = _("Can not get more %s.") % object_record.name
                            break

                        # Get the number that actually added.
                        add = number
                        if add > object_record.max_stack:
                            add = object_record.max_stack

                        # add a new object to the inventory
                        await add_new_object(object_key, level, add, object_record.element_type, object_record.can_remove)

                        number -= add
                        accepted += add

            objects.append({
                "key": object_record.key,
                "name": object_record.name,
                "icon": object_record.icon,
                "number": accepted,
                "reject": reject,
            })

        results = {
            "objects": objects
        }

        # call quest handler
        awaits = [
            self.quest_handler.at_objective(defines.OBJECTIVE_OBJECT, obj["key"], obj["number"]) for obj in objects
            if not obj["reject"]
        ]

        if awaits:
            # Get accomplished quests.
            quest_results = await async_gather(awaits)

            # Remove empty quests.
            quest_results = [r for r in quest_results if r]

            if quest_results:
                quests = {}
                for r in quest_results:
                    for key, value in r.items():
                        if key in quests:
                            quests[key].append(value)
                        else:
                            quests[key] = value

                results["quests"] = quests

        return results

    def can_get_object(self, obj_key, number):
        """
        Check if the character can get these objects.

        Args:
            obj_key: (String) object's key
            number: (int) object's number

        Returns:
            boolean: can get

        Notice:
            If the character does not have this object, the return will be always true,
            despite of the number!
        """
        try:
            common_models = ELEMENT("POCKET_OBJECT").get_models()
            object_record = WorldData.get_tables_data(common_models, key=obj_key)
            object_record = object_record[0]
        except Exception as e:
            return False

        total = self.total_object_number(obj_key)
        if not total:
            return True

        if not object_record.unique:
            return True

        if total + number <= object_record.max_stack:
            return True

        return False

    async def get_inventory_obj_by_pos(self, position):
        """
        Get an object in the inventory
        :param position:
        :return:
        """
        if position not in self.inventory:
            return None

        item = self.inventory[position]
        if "obj" in item and item["obj"]:
            return item["obj"]
        else:
            new_obj = ELEMENT(item["element_type"])()
            await new_obj.setup_element(item["object_key"], item["level"])
            item["obj"] = new_obj
            return new_obj

    async def get_inventory_obj_by_key(self, obj_key):
        """
        Get an object in the inventory
        :param obj_key: (string) the key of an object in the inventory
        :return:
        """
        for item in self.inventory.values():
            if item["object_key"] == obj_key:
                if "obj" in item and item["obj"]:
                    return item["obj"]
                else:
                    new_obj = ELEMENT(item["element_type"])()
                    await new_obj.setup_element(item["object_key"], item["level"])
                    item["obj"] = new_obj
                    return new_obj

        return None

    async def use_object(self, position, number=1):
        """
        Use an object.

        Args:
            position: (int) object's position in the inventory
            number: (int) number to use

        Returns:
            result: (string) the description of the result
        """
        if position not in self.inventory:
            raise MudderyError(_("Can not find this object."))

        item = self.inventory[position]
        if item["number"] < number:
            raise MudderyError(_("Not enough number."))

        item_obj = await self.get_inventory_obj_by_pos(position)

        # take effect
        result, used = await item_obj.take_effect(self, number)
        if used > 0:
            # remove used object
            await self.remove_objects_by_position(position, used)

        return result

    async def remove_all_objects_by_position(self, position):
        """
        Remove all objects by its position.

        :param position:
        :return:
        """
        if position not in self.inventory:
            raise MudderyError(_("Can not find this object."))

        item = self.inventory[position]
        if item["can_remove"]:
            await CharacterInventory.inst().remove_object(self.get_db_id(), position)
            del self.inventory[position]
        else:
            await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": 0})
            item["number"] = 0

        return

    async def remove_objects_by_position(self, position, number):
        """
        Remove objects by its position.

        :param obj_id:
        :return:
        """
        if position not in self.inventory:
            raise MudderyError(_("Can not find this object."))

        if number <= 0:
            raise MudderyError(_("Can not remove by %s.") % number)

        item = self.inventory[position]
        obj_num = item["number"]
        if obj_num > number:
            await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": obj_num - number})
            item["number"] = obj_num - number
        elif obj_num == number:
            if item["can_remove"]:
                await CharacterInventory.inst().remove_object(self.get_db_id(), position)
                del self.inventory[position]
            else:
                await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": 0})
                item["number"] = 0
        else:
            raise (MudderyError(_("Can not remove this object.")))

        return

    async def remove_all_objects_by_key(self, obj_key):
        """
        Remove all objects of this object_key.
        """
        to_remove = []
        for position, item in self.inventory.items():
            if item["object_key"] == obj_key:
                to_remove.append(position)

        for position in to_remove:
            if self.inventory[position]["can_remove"]:
                await CharacterInventory.inst().remove_object(self.get_db_id(), position)
                del self.inventory[position]
            else:
                await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": 0})
                self.inventory[position]["number"] = 0

        return

    async def remove_objects_by_key(self, obj_key, number):
        """
        Remove all objects of this object_key.
        """
        if number <= 0:
            raise MudderyError(_("Can not remove by %s.") % number)

        # Count objects in the inventory.
        total = sum([item["number"] for item in self.inventory.values() if obj_key == item["object_key"]])
        if total < number:
            raise (MudderyError(_("Can not remove this object.")))

        to_remove = []
        for position, item in self.inventory.items():
            if item["object_key"] == obj_key:
                to_remove.append(position)

        for position in to_remove:
            item = self.inventory[position]
            obj_num = item["number"]
            if obj_num > number:
                await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": obj_num - number})
                item["number"] = obj_num - number
                number = 0
            else:
                number -= obj_num
                if item["can_remove"]:
                    await CharacterInventory.inst().remove_object(self.get_db_id(), position)
                    del self.inventory[position]
                else:
                    await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": 0})
                    item["number"] = 0

            if number == 0:
                break

        return

    async def remove_objects_by_list(self, obj_list):
        """
        Remove objects from the inventory.

        Args:
            obj_list: (list) a list of object keys and there numbers.
                             list item: {"object": object's key
                                         "number": object's number}

        Returns:
            boolean: success
        """
        for item in obj_list:
            await self.remove_objects_by_key(item["object_key"], item["number"])

        return obj_list

    async def exchange_objects(self, remove_list, receive_list):
        """
        Exchange some objects to other objects.

        :param remove_list:
        :param receive_list:
        :return:
        """
        with self.states.transaction():
            remove = await self.remove_objects_by_list(remove_list)
            receive = await self.receive_objects(receive_list)

        return {
            "use": remove,
            "get": receive,
        }

    def get_inventory_appearance(self):
        """
        Get the inventory's appearance to the player.
        """
        inv = []

        # load object's data
        common_models = ELEMENT("POCKET_OBJECT").get_models()

        for position, item in self.inventory.items():
            object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
            object_record = object_record[0]

            info = {
                "position": item["position"],       # item's position
                "number": item["number"],           # item's number
                "level": item["level"],             # item's level
                "can_remove": item["can_remove"],
                "name": object_record.name,         # item's name
                "desc": object_record.desc,         # item's desc
                "icon": object_record.icon,         # item's icon
            }
            inv.append(info)

        return inv

    async def get_inventory_object_appearance(self, position):
        """
        Get inventory's data.
        """
        try:
            item = self.inventory[position]
        except KeyError:
            raise MudderyError(ERR.invalid_input, _("Can not find it in your inventory."))

        item_obj = await self.get_inventory_obj_by_pos(position)

        appearance = await item_obj.get_detail_appearance(self)
        appearance["number"] = item["number"]
        appearance["position"] = position

        # add a discard command
        if item_obj.can_discard():
            appearance["cmds"].append({
                "name": _("Discard"),
                "cmd": "discard",
                "confirm": _("Discard this object?"),
            })
        return appearance

    async def return_equipments_object(self, position):
        """
        Get equipments data.
        """
        try:
            item = self.equipments[position]
        except KeyError:
            raise MudderyError(ERR.invalid_input, _("Can not find it in your equipments."))

        appearance = await item["obj"].get_detail_appearance(self)

        # add a take off command, remove equip command
        commands = [c for c in appearance["cmds"] if c["cmd"] != "equip"]
        commands.append({
            "name": _("Take Off"),
            "cmd": "takeoff",
            "args": {
                "position": position
            },
        })
        appearance["cmds"] = commands

        return appearance

    async def get_state(self):
        """
        Get character's state.
        """
        state = {
            "level": {
                "name": _("LEVEL"),
                "value": await self.get_level(),
            }
        }

        state.update({
            key: {
                "name": info["name"],
                "value": self.const_data_handler.get(key),
            } for key, info in self.get_properties_info().items()
        })

        records = CharacterStatesDict.all()
        state.update({
            record.key: {
                "name": record.name,
                "value": await self.states.load(record.key)
            } for record in records
        })

        return state

    async def load_equipments(self):
        """
        Reset equipment's position data.

        equipments: {
            position on the body: {
                "object_key": object's key,
                "level": object's level,
                "obj": object's instance,
            }
        }
        Returns:
            None
        """
        self.equipments = await CharacterEquipments.inst().get_character(self.get_db_id())

        # get equipment's position
        positions = set([r.key for r in EquipmentPositions.all()])
        common_models = ELEMENT("POCKET_OBJECT").get_models()

        take_off = []
        for pos in list(self.equipments.keys()):
            if pos in positions:
                # create an instance of the equipment
                item = self.equipments[pos]

                object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
                object_record = object_record[0]
                item["element_type"] = object_record.element_type

                new_obj = ELEMENT(item["element_type"])()
                item["obj"] = new_obj
            else:
                # the position has been removed, take off the equipment.
                take_off.append(pos)

        awaits = [
            item["obj"].setup_element(item["object_key"], item["level"]) for item in self.equipments.values()
            if item["obj"]
        ]
        if awaits:
            await async_wait(awaits)

        if take_off:
            await async_wait([self.take_off_equipment(pos, refresh=False) for pos in take_off])

    def get_equipments(self):
        """
        Get equipments' data.
        """
        info = {}
        for pos, item in self.equipments.items():
            # order by positions
            info[pos] = item["obj"].get_appearance()

        return info

    async def equip_object(self, position):
        """
        Equip an object.
        args: position: (int) position in the inventory
        """
        if position not in self.inventory:
            raise MudderyError(_("Can not find this equipment."))

        item = self.inventory[position]

        body_position = item["obj"].get_body_position()
        available_positions = set([r.key for r in EquipmentPositions.all()])
        if body_position not in available_positions:
            raise MudderyError(_("Can not equip it on this position."))

        # Take off old equipment
        if body_position in self.equipments:
            await self.take_off_equipment(body_position, refresh=False)

        # Put on new equipment.
        if "obj" not in item or not item["obj"]:
            # create an instance of the equipment
            new_obj = ELEMENT(item["element_type"])()
            await new_obj.setup_element(item["object_key"], item["level"])
            item["obj"] = new_obj

        obj_num = item["number"]
        with self.states.transaction():
            # add to body
            await CharacterEquipments.inst().add(self.get_db_id(), body_position, item["object_key"], item["level"])

            # Remove from the inventory
            if obj_num > 1:
                await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": obj_num - 1})
                item["number"] = obj_num - 1
            elif obj_num == 1:
                if item["can_remove"]:
                    await CharacterInventory.inst().remove_object(self.get_db_id(), position)
                    del self.inventory[position]
                else:
                    await CharacterInventory.inst().set_dict(self.get_db_id(), position, {"number": 0})
                    item["number"] = 0

        self.equipments[body_position] = item

        # reset character's attributes
        await self.refresh_states(True)

    async def take_off_equipment(self, body_position, refresh=True):
        """
        Take off an equipment.
        args:
            position: (string) a position on the body.
        """
        if body_position not in self.equipments:
            raise MudderyError(_("Can not find this equipment."))

        item = self.equipments[body_position]

        # Move to the inventory
        common_models = ELEMENT("POCKET_OBJECT").get_models()
        try:
            object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
            object_record = object_record[0]
        except Exception as e:
            logger.log_err("Can not find object %s: %s" % (item["object_key"], e))
            raise MudderyError(_("Can not take off this equipment."))

        if len(self.inventory) > 0:
            new_position = sorted(self.inventory)[-1] + 1
        else:
            new_position = 1

        # save to db first
        with self.states.transaction():
            await CharacterInventory.inst().add(self.get_db_id(), new_position, item["object_key"], 1, item["level"])
            await CharacterEquipments.inst().remove_equipment(self.get_db_id(), body_position)

            # add to the inventory
            self.inventory[new_position] = {
                "position": new_position,
                "object_key": item["object_key"],
                "level": item["level"],
                "number": 1,
                "element_type": object_record.element_type,
                "can_remove": object_record.can_remove,
            }

        # remove from body
        del self.equipments[body_position]

        if refresh:
            # reset character's attributes
            await self.refresh_states(True)

    async def lock_exit(self, exit_key):
        """
        Lock an exit. Remove the exit's key from the character's unlock list.
        """
        unlocked_exits = await self.states.load("unlocked_exits", set())
        if exit_key not in unlocked_exits:
            return

        unlocked_exits.remove(exit_key)
        await self.states.save("unlocked_exits", unlocked_exits)

    async def unlock_exit(self, exit_key) -> bool:
        """
        Unlock an exit. Add the exit's key to the character's unlock list.
        """
        unlocked_exits = await self.states.load("unlocked_exits", set())
        if exit_key in unlocked_exits:
            return True

        if not await self.location.can_unlock_exit(self, exit_key):
            return False

        unlocked_exits.add(exit_key)
        await self.states.save("unlocked_exits", unlocked_exits)

        return True

    async def is_exit_unlocked(self, exit_key):
        """
        Whether the exit is unlocked.
        """
        unlocked_exits = await self.states.load("unlocked_exits", set())
        return exit_key in unlocked_exits

    async def load_skills(self):
        """
        Load character's skills.
        """
        self.skills = {}

        # default skills
        default_skills = DefaultSkills.get(self.get_element_key())
        default_skill_set = set([r.skill for r in default_skills])

        # current skills
        character_skills = await CharacterSkills.inst().load_character(self.get_db_id())

        to_delete = []
        to_save = []
        for key, item in character_skills.items():
            if item["is_default"] and key not in default_skill_set:
                # default skill is deleted, remove it from db
                to_delete.append(key)
                continue

            # Store new skill.
            self.skills[key] = {
                "level": item["level"],
                "cd_finish": 0,
            }

        # add new default skills
        for item in default_skills:
            key = item.skill
            if key not in self.skills:
                # Store new skill.
                self.skills[key] = {
                    "level": item.level,
                    "cd_finish": 0,
                }

                # save skill
                await CharacterSkills.inst().save(self.get_db_id(), key, {
                    "level": item.level,
                    "is_default": True,
                    "cd_finish": 0,
                })

        if to_delete:
            await async_wait([CharacterSkills.inst().delete(self.get_db_id(), key) for key in to_delete])

        if to_save:
            await async_wait([CharacterSkills.inst().save(self.get_db_id(), key, self.skills["level"], True, 0) for key in to_save])

        if self.skills:
            skills = await async_gather([self.create_skill(key, item["level"]) for key, item in self.skills.items()])
            for index, item in enumerate(self.skills.values()):
                item["obj"] = skills[index]

    async def learn_skill(self, skill_key, level):
        """
        Learn a new skill.

        Args:
            skill_key: (string) skill's key
            level: (number) skill's level

        Returns:
            (boolean) learned skill
        """
        if skill_key in self.skills:
            raise MudderyError(ERR.invalid_input, _("You have already learned this skill."))

        try:
            # Create skill object.
            skill_obj = ELEMENT("SKILL")()
            await skill_obj.setup_element(skill_key, level)
        except Exception as e:
            logger.log_err("Can not learn skill %s: (%s) %s" % (skill_key, type(e).__name__, e))
            raise MudderyError(ERR.invalid_input, _("Can not learn this skill."))

        # Store new skill.
        self.skills[skill_key] = {
            "obj": skill_obj,
            "cd_finish": 0,
        }

        # save skill
        await CharacterSkills.inst().save(self.get_db_id(), skill_key, {
            "level": level,
            "is_default": False,
            "cd_finish": 0,
        })

        # If it is a passive skill, player's status may change.
        if skill_obj.passive:
            await self.refresh_states(True)

        return {
            "key": skill_key,
            "name": skill_obj.get_name(),
        }

    def get_skills(self):
        """
        Get skills' data.
        """
        skills_list = []

        for skill in self.skills.values():
            skills_list.append(skill["obj"].get_appearance())

        return skills_list

    async def cast_passive_skills(self):
        """
        Cast all passive skills.
        """
        awaits = [skill["obj"].cast(self, self) for skill in self.skills.values() if skill["obj"].is_passive()]
        if awaits:
            await async_wait(awaits)

    async def cast_skill(self, skill_key, target):
        """
        Cast a skill.

        Args:
            skill_key: (string) skill's key.
            target: (object) skill's target.
        """
        last_cd_finish = self.skills[skill_key]["cd_finish"]
        result = await super(MudderyPlayerCharacter, self).cast_skill(skill_key, target)
        cd_finish = self.skills[skill_key]["cd_finish"]

        if last_cd_finish != cd_finish:
            await CharacterSkills.inst().save(self.get_db_id(), skill_key, {"cd_finish": cd_finish})

        return result

    async def close_event(self, event_key):
        """
        If an event is closed, it will never be triggered.

        Args:
            event_key: (string) event's key
        """
        # set closed events
        await CharacterClosedEvents.inst().add(self.get_db_id(), event_key)

    async def is_event_closed(self, event_key):
        """
        Return True If this event is closed.

        Args:
            event_key: (string) event's key
        """
        return await CharacterClosedEvents.inst().has(self.get_db_id(), event_key)

    async def all_closed_events(self):
        """
        Get all closed events.
        """
        return await CharacterClosedEvents.inst().get_character(self.get_db_id())

    async def join_combat(self, combat_id):
        """
        The character joins a combat.

        :param combat_id: (int) combat's id.
        :return:
        """
        await super(MudderyPlayerCharacter, self).join_combat(combat_id)
        await CharacterCombat.inst().save(self.get_db_id(), combat_id)

    async def get_combat(self):
        """
        Get the character's combat. If the character is not in combat, return None.
        :return:
        """
        if self.combat_id is None:
            return None

        combat = COMBAT_HANDLER.get_combat(self.combat_id)
        if combat is None:
            # Combat is finished.
            self.combat_id = None
            await CharacterCombat.inst().remove_character(self.get_db_id())

        return combat

    async def get_last_combat(self):
        """
        Get unfinished combat.

        Returns:
            None
        """
        combat = await self.get_combat()
        if combat:
            if combat.is_finished():
                await self.leave_combat()
            else:
                # show combat information
                return {
                    "combat_info": combat.get_appearance(),
                    "combat_commands": self.get_combat_commands(),
                    "combat_states": await combat.get_combat_states(),
                }

    async def combat_result(self, combat_type, result, opponents=None, rewards=None):
        """
        Set the combat result.

        :param combat_type: combat's type
        :param result: defines.COMBAT_WIN, defines.COMBAT_LOSE, or defines.COMBAT_DRAW
        :param opponents: combat opponents
        :param rewards: combat rewards
        """
        combat_result = {
            "type": combat_type.value,
            "result": result,
            "rewards": {},
        }

        # get rewards
        if rewards:
            if "exp" in rewards and rewards["exp"]:
                exp = rewards["exp"]
                exp_results = await self.add_exp(exp)
                combat_result["rewards"]["exp"] = exp
                combat_result["rewards"].update(exp_results)

            # give objects to winner
            if "loots" in rewards and rewards["loots"]:
                get_objects = await self.receive_objects(rewards["loots"])
                combat_result["rewards"]["get_objects"] = get_objects

            # honours
            if "honour" in rewards and rewards["honour"]:
                combat_result["rewards"]["honour"] = rewards["honour"]

        # set state
        if "level_up" in combat_result["rewards"] or combat_type == CombatType.HONOUR:
            # recover state
            await self.recover()
            combat_result["state"] = await self.get_state()

        await self.msg({"combat_finish": combat_result})

    async def leave_combat(self):
        """
        Leave the current combat.
        """
        status = None
        opponents = None
        rewards = None

        combat = await self.get_combat()
        if not combat:
            return

        combat_result = combat.get_combat_result(self.id)
        if combat_result:
            status, opponents, rewards = combat_result

        event_results = []
        quest_results = []
        results = {}

        combat_type = combat.get_combat_type()
        if combat_type == CombatType.NORMAL:
            # normal combat
            # trigger events
            if status == defines.COMBAT_WIN:
                if opponents:
                    event_results = await async_gather([self.event.at_character_kill(op) for op in opponents])
                    quest_results = await async_gather([self.quest_handler.at_objective(defines.OBJECTIVE_KILL, op.get_element_key())
                                                         for op in opponents])
            elif status == defines.COMBAT_LOSE:
                await self.die(opponents)
                event_results = await self.event.at_character_die()
                results["die"] = True
                if self.reborn_time > 0:
                    results["reborn_time"] = self.reborn_time
        elif combat_type == CombatType.HONOUR:
            if status == defines.COMBAT_WIN:
                await self.honour_win()
            elif status == defines.COMBAT_LOSE:
                await self.honour_lose()

        await combat.leave_combat(self)
        self.combat_id = None
        await CharacterCombat.inst().remove_character(self.get_db_id())

        # Remove empty events.
        events = [e for event_list in event_results if event_list for e in event_list]
        if events:
            results["events"] = events

        # Remove empty quests.
        quest_results = [r for r in quest_results if r]

        if quest_results:
            quests = {}
            for r in quest_results:
                for key, value in r.items():
                    if key in quests:
                        quests[key].append(value)
                    else:
                        quests[key] = value

            results["quests"] = quests

        return results

    async def die(self, killers):
        """
        This character is killed. Move it to it's home.
        """

        # player's character can always reborn
        if self.reborn_time < 1:
            self.reborn_time = 1

        await super(MudderyPlayerCharacter, self).die(killers)

    async def honour_win(self):
        """
        The character win in an honour combat.
        """
        pass


    async def honour_lose(self):
        """
        The character lost in an honour combat.
        """
        pass

    async def reborn(self):
        """
        Reborn after being killed.
        """
        # Recover properties.
        await self.recover()
        self.is_alive = True

        # Reborn at its home.
        home = None
        default_home_key = GameSettings.inst().get("default_player_home_key")
        if default_home_key:
            try:
                home = Server.world.get_room(default_home_key)
            except KeyError:
                pass

        if home:
            await self.move_to(home)
            await self.msg({
                "msg": _("You are reborn at {C%s{n.") % home.get_name(),
                "move_to": {
                    "location": self.get_location_info(),
                    "look_around": self.look_around(),
                }
            })
        else:
            await self.msg({"msg": _("You are reborn.")})

    async def save_current_dialogues(self, current_dialogue):
        """
        Save player's current dialogues.

        Args:
            current_dialogue: current dialogues

        Returns:
            None
        """
        # Save the dialogue's key.
        if current_dialogue:
            self.current_dialogues = set([d["key"] for d in current_dialogue["dialogues"]])
        else:
            self.current_dialogues = set()

        if not GameSettings.inst().get("auto_resume_dialogues"):
            # Can not auto resume dialogues.
            return

        await self.states.save("current_dialogue", current_dialogue if current_dialogue else None)
        return

    async def get_last_dialogue(self):
        """
        Restore player's dialogues when he return to game.

        Returns:
            None
        """
        if not GameSettings.inst().get("auto_resume_dialogues"):
            # Can not auto resume dialogues.
            return

        return await self.states.load("current_dialogue")

    async def talk_to_npc(self, npc):
        """
        Talk to an NPC.

        Args:
            npc: NPC's object.

        Returns:
            None
        """
        # Get NPC's dialogue list.
        dialogues = await DialogueHandler.inst().get_npc_dialogues(self, npc)

        await self.save_current_dialogues(dialogues)

        return dialogues

    async def start_dialogue(self, dlg_key):
        """
        Start a dialogue.

        Args:
            dlg_key: dialogue's key.

        Returns:
            None
        """
        # Get next sentences_list.
        dialogue = await DialogueHandler.inst().get_dialogues_by_key(dlg_key)

        # Send the dialogue to the player.
        await self.save_current_dialogues(dialogue)

        return dialogue

    async def finish_dialogue(self, dlg_key, npc):
        """
        Continue current dialogue.

        Args:
            dlg_key: current dialogue's key.
            npc: (optional) NPC's object.

        Returns:
            None
        """
        if dlg_key not in self.current_dialogues:
            logger.log_err("Not in current dialogues: %s" % dlg_key)
            return

        results = {}
        try:
            # Finish current dialogue
            results = await DialogueHandler.inst().finish_dialogue(dlg_key, self, npc)
        except Exception as e:
            logger.log_trace("Can not finish dialogue %s: %s" % (dlg_key, e))

        # Get next dialogue.
        next_dialogues = await DialogueHandler.inst().get_next_dialogues(dlg_key, self, npc)
        results["dialogue"] = next_dialogues

        # Send dialogues_list to the player.
        await self.save_current_dialogues(next_dialogues)

        return results

    async def get_message(self, caller, message):
        """
        Receive a message from a character.

        :param caller: talker.
        :param message: content.
        """
        output = {
            "type": ConversationType.PRIVATE.value,
            "channel": self.get_name(),
            "from_id": caller.get_id(),
            "from_name": caller.get_name(),
            "msg": message
        }

        await async_wait([
            self.msg({"conversation": output}),
            caller.msg({"conversation": output}),
        ])

    async def get_honour_rankings(self):
        """
        Show character's rankings.
        """
        honour_settings = HonourSettings.get_first_data()
        top_rankings = HonoursMapper.inst().get_top_rankings(honour_settings.top_rankings_number)
        nearest_rankings = HonoursMapper.inst().get_nearest_rankings(self, honour_settings.nearest_rankings_number)

        rankings = top_rankings
        rankings.extend([char_id for char_id in nearest_rankings if char_id not in top_rankings])

        nicknames = await async_gather([CharacterInfo.inst().get_nickname(char_id) for char_id in rankings])

        return [{
            "name": nicknames[index],
            "id": char_id,
            "ranking": HonoursMapper.inst().get_ranking(char_id),
            "honour": HonoursMapper.inst().get_honour(char_id),
        } for index, char_id in enumerate(rankings)]

    async def get_quest_info(self, quest_key):
        """
        Get a quest's detail information.
        :param quest_key:
        :return:
        """
        return await self.quest_handler.get_quest_info(quest_key)

    async def get_skill_info(self, skill_key):
        """
        Get a skill's detail information.
        :param skill_key:
        :return:
        """
        try:
            return await self.skills[skill_key]["obj"].get_detail_appearance(self)
        except KeyError:
            raise MudderyError(ERR.invalid_input, _("Can not find the skill."))

    async def get_relationship(self, element_type, element_key):
        """
        Get the relationship value between the player and the element.
        :param element_type:
        :param element_key:
        :return:
        """
        return await CharacterRelationships.inst().load(self.get_db_id(), element_type, element_key, None)

    async def set_relationship(self, element_type, element_key, relationship):
        """
        Get the relationship value between the player and the element.
        :param element_type:
        :param element_key:
        :param relationship: relationship's value
        :return:
        """
        await CharacterRelationships.inst().save(self.get_db_id(), element_type, element_key, relationship)
        # todo: get other element's name
        records = Characters.get_data(element_key)
        return {
            "key": element_key,
            "name": records[0].name if records else "",
            "value": relationship,
        }

    async def increase_relationship(self, element_type, element_key, value):
        """
        Add the relationship value between the player and the element with the given number.
        :param element_type:
        :param element_key:
        :return:
        """
        await CharacterRelationships.inst().increase(self.get_db_id(), element_type, element_key, value)
        # todo: get other element's name
        records = Characters.get_data(element_key)
        return {
            "key": element_key,
            "name": records[0].name if records else "",
            "value": value,
        }
