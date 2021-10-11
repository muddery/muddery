"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import ast, traceback
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.scripts.scripthandler import ScriptHandler
from evennia.commands.cmdsethandler import CmdSetHandler
from evennia.utils.utils import lazy_property
from evennia.utils import logger
from evennia.comms.models import ChannelDB
from muddery.server.server import Server
from muddery.server.utils.quest_handler import QuestHandler
from muddery.server.utils.statement_attribute_handler import StatementAttributeHandler
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.server.utils.defines import ConversationType
from muddery.server.utils.defines import CombatType
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.default_skills import DefaultSkills
from muddery.server.database.worlddata.honour_settings import HonourSettings
from muddery.server.database.worlddata.default_objects import DefaultObjects
from muddery.server.database.worlddata.element_properties import ElementProperties
from muddery.server.database.worlddata.equipment_positions import EquipmentPositions
from muddery.server.database.worlddata.character_states_dict import CharacterStatesDict
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils import defines
from muddery.server.utils.data_field_handler import DataFieldHandler, ConstDataHolder
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.database.gamedata.honours_mapper import HONOURS_MAPPER
from muddery.server.database.gamedata.character_inventory import CharacterInventory
from muddery.server.database.gamedata.character_equipments import CharacterEquipments
from muddery.server.database.gamedata.character_info import CharacterInfo
from muddery.server.database.gamedata.character_skills import CharacterSkills
from muddery.server.database.gamedata.character_combat import CharacterCombat
from muddery.server.database.gamedata.character_location import CharacterLocation
from muddery.server.combat.match_pvp import MATCH_COMBAT_HANDLER
from muddery.server.utils.object_states_handler import ObjectStatesHandler
from muddery.server.database.gamedata.object_storage import DBObjectStorage
from muddery.server.events.event_trigger import EventTrigger


class MudderyPlayerCharacter(ELEMENT("CHARACTER")):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    element_type = "PLAYER_CHARACTER"
    element_name = _("Player Character", "elements")
    model_name = "player_characters"

    def __init__(self):
        """
        Initial the object.
        """
        super(MudderyPlayerCharacter, self).__init__()

        self.pk = 0

        self.session = None
        self.account_id = None

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

    def __str__(self):
        """
        Print the character's name.
        :return:
        """
        return "%s(%s)" % (self.get_name(), self.get_id())

    # initialize all handlers in a lazy fashion
    @lazy_property
    def event(self):
        return EventTrigger(self)

    @lazy_property
    def states(self):
        return ObjectStatesHandler(self.get_db_id(), DBObjectStorage)

    @lazy_property
    def cmdset(self):
        return CmdSetHandler(self, True)

    # cmdset_storage property handling
    def __cmdset_storage_get(self):
        """getter"""
        return [settings.CMDSET_CHARACTER]

    def __cmdset_storage_set(self, value):
        """setter"""
        pass

    def __cmdset_storage_del(self):
        """deleter"""
        pass

    cmdset_storage = property(__cmdset_storage_get, __cmdset_storage_set, __cmdset_storage_del)

    def contents_get(self, exclude=None):
        """
        Returns the contents of this object, i.e. all
        objects that has this object set as its location.
        This should be publically available.

        Args:
            exclude (Object): Object to exclude from returned
                contents list

        Returns:
            contents (list): List of contents of this Object.

        Notes:
            Also available as the `contents` property.

        """
        return []

    def contents_set(self, *args):
        "You cannot replace this property"
        raise AttributeError(
            "{}.contents is read-only. Use obj.move_to or "
            "obj.location to move an object here.".format(self.__class__)
        )

    contents = property(contents_get, contents_set, contents_set)

    # initialize all handlers in a lazy fashion
    @lazy_property
    def quest_handler(self):
        return QuestHandler(self)

    # attributes used in statements
    @lazy_property
    def statement_attr(self):
        return StatementAttributeHandler(self)

    @lazy_property
    def body_data_handler(self):
        return DataFieldHandler(self)

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

    def set_level(self, level):
        """
        Set element's level.
        :param level:
        :return:
        """
        if self.level == level:
            return

        CharacterInfo.set_level(self.get_db_id(), level)
        super(MudderyPlayerCharacter, self).set_level(level)

    def setup_element(self, key, level=None, first_time=False, temp=False):
        """
        Set element data's key.

        Args:
            key: (string) the key of the data.
            level: (int) element's level.
        """
        if level is None:
            level = CharacterInfo.get_level(self.get_db_id())

        super(MudderyPlayerCharacter, self).setup_element(key, level, first_time)

    def at_element_setup(self, first_time):
        """
        Called when the element is setting up.

        :arg
            first_time: (bool) the first time to setup the element.
        """
        super(MudderyPlayerCharacter, self).at_element_setup(first_time)

        # load inventory
        self.load_inventory()

        # load equipments
        self.load_equipments()

        self.solo_mode = GAME_SETTINGS.get("solo_mode")
        self.available_channels = {}
        self.current_dialogues = set()

    def after_element_setup(self, first_time):
        """
        Called after the element is setting up.

        :arg
            first_time: (bool) the first time to setup the element.
        """
        super(MudderyPlayerCharacter, self).after_element_setup(first_time)

        # if it is dead, reborn at init.
        if not self.is_alive():
            if not self.is_temp and self.reborn_time > 0:
                self.reborn()

        # load combat id
        self.combat_id = CharacterCombat.load(self.get_db_id(), None)

    def load_custom_level_data(self, element_type, element_key, level):
        """
        Load body properties from db.
        """
        # Get object level.
        super(MudderyPlayerCharacter, self).load_custom_level_data(element_type, element_key, level)

        # Set body values.
        for key, info in self.get_properties_info().items():
            value = self.const_data_handler.get(key)
            self.body_data_handler.add(key, value)

    def set_session(self, session):
        """
        Set the client's session.
        :param session:
        :return:
        """
        self.session = session

    def set_account_id(self, account_id):
        """
        Set the player's account id.
        :param account_id:
        :return:
        """
        self.account_id = account_id

    def get_account_id(self):
        """
        Get the player's account id.
        :return:
        """
        return self.account_id

    def move_to(self, location):
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
        CharacterLocation.save(self.get_db_id(), location_key)

        if self.location:
            self.location.at_character_leave(self)

        self.set_location(location)

        # Send new location's data to the character.
        location_name = self.location.name if location else ""
        self.msg({"msg": _("Moved to %s ...") % location_name})
        self.show_location()

        if self.location:
            self.location.at_character_arrive(self)

        # Trigger the arrive event.
        if self.location:
            self.event.at_character_move_in(self.location)
            self.quest_handler.at_objective(defines.OBJECTIVE_ARRIVE, location_key)

    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        self.available_channels = self.get_available_channels()

        # send character's data to player
        message = {
            "status": self.return_status(),
            "equipments": self.return_equipments(),
            "inventory": self.get_inventory_appearance(),
            "skills": self.return_skills(),
            "quests": self.quest_handler.return_quests(),
            "revealed_map": self.get_revealed_map(),
            "channels": self.available_channels
        }
        self.msg(message)

        self.show_location()

        self.resume_last_dialogue()

        self.resume_combat()

        # Resume all scripts.
        #scripts = self.scripts.all()
        #for script in scripts:
        #    script.unpause()

    def at_pre_unpuppet(self):
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
                self.location.at_character_leave(self)

        MATCH_COMBAT_HANDLER.remove(self)

    def refresh_states(self, keep_states):
        """
        Refresh character's states.

        Args:
            keep_states (boolean): states values keep last values.
        """
         # Load body properties.
        for key, value in self.body_data_handler.all().items():
            self.const_data_handler.add(key, value)

        if not keep_states:
            super(MudderyPlayerCharacter, self).refresh_states(False)

        # load equips
        self.wear_equipments()

        # load passive skills
        self.cast_passive_skills()

        super(MudderyPlayerCharacter, self).refresh_states(keep_states)

    def msg(self, text=None, options=None, **kwargs):
        """
        Emits something to a session attached to the object.

        Args:
            text (str, optional): The message to send

        Notes:
            `at_msg_receive` will be called on this Object.
            All extra kwargs will be passed on to the protocol.
        """
        if not self.session:
            return

        # Send messages to the client. Messages are in format of JSON.
        kwargs["options"] = options

        # relay to session
        logger.log_info("Send message, %s: %s" % (self.get_db_id(), text))
        self.session.msg(text=text, **kwargs)

    def get_level(self):
        """
        Get the character's level.
        :return:
        """
        return CharacterInfo.get_level(self.get_db_id())

    def set_nickname(self, nickname):
        """
        Set player character's nickname.
        """
        CharacterInfo.set_nickname(self.get_db_id(), nickname)

    def get_name(self):
        """
        Get player character's name.
        """
        # Use nick name instead of normal name.
        return CharacterInfo.get_nickname(self.get_db_id())

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive():
            commands.append({"name": _("Attack"), "cmd": "attack", "args": self.get_id()})
        return commands

    def get_available_channels(self):
        """
        Get available channel's info.

        Returns:
            (dict) channels
        """
        channels = {}
        channel = ChannelDB.objects.get_channel(settings.DEFAULT_CHANNELS[0]["key"])
        if channel.has_connection(self):
            channels[channel.key] = {
                "type": "CHANNEL",
                "name": _("Public", category="channels"),
            }

        return channels

    def get_revealed_map(self):
        """
        Get the map that the character has revealed.
        Return value:
            {
                "rooms": {room1's key: {"name": name,
                                        "icon": icon,
                                        "area": area,
                                        "pos": position},
                          room2's key: {"name": name,
                                        "icon": icon,
                                        "area": area,
                                        "pos": position},
                          ...},
                "exits": {exit1's key: {"from": room1's key,
                                        "to": room2's key},
                          exit2's key: {"from": room3's key,
                                        "to": room4's key},
                          ...}
            }
        """
        rooms = {}
        exits = {}

        revealed_map = self.states.load("revealed_map", set())
        for room_key in revealed_map:
            # get room's information
            try:
                room = Server.world.get_room(room_key)
                area = Server.world.get_area_by_room(room_key)
                rooms[room_key] = {"name": room.get_name(),
                                   "icon": room.icon,
                                   "area": area.get_element_key(),
                                   "pos": room.position}
                new_exits = room.get_exits()
                if new_exits:
                    exits.update(new_exits)
            except ObjectDoesNotExist:
                pass

        for path in exits.values():
            # add room's neighbours
            if not path["to"] in rooms:
                try:
                    neighbour_room = Server.world.get_room(path["to"])
                    neighbour_area = Server.world.get_area_by_room(path["to"])
                    rooms[neighbour_room.get_element_key()] = {
                        "name": neighbour_room.get_name(),
                        "icon": neighbour_room.icon,
                        "area": neighbour_area.get_element_key(),
                        "pos": neighbour_room.position
                    }
                except ObjectDoesNotExist:
                    pass

        return {"rooms": rooms, "exits": exits}

    def wear_equipments(self):
        """
        Add equipment's attributes to the character
        """
        # add equipment's attributes
        for item in self.equipments.values():
            item["obj"].equip_to(self)

    def show_location(self):
        """
        show character's location
        """
        if not self.location:
            return

        location_key = self.location.get_element_key()
        area = Server.world.get_area_by_room(location_key)

        msg = {
            "current_location": {
                "key": location_key,
                "area": area.get_appearance(self),
            }
        }

        """
        reveal_map:
        {
            "rooms": {room1's key: {"name": name,
                                    "icon": icon,
                                    "area": area,
                                    "pos": position},
                      room2's key: {"name": name,
                                    "icon": icon,
                                    "area": area,
                                    "pos": position},
                      ...},
            "exits": {exit1's key: {"from": room1's key,
                                    "to": room2's key},
                      exit2's key: {"from": room3's key,
                                    "to": room4's key},
                      ...}
        }
        """
        revealed_map = self.states.load("revealed_map", set())
        if not location_key in revealed_map:
            # reveal map
            revealed_map.add(self.location.get_element_key())
            self.states.save("revealed_map", revealed_map)

            rooms = {
                location_key: {
                    "name": self.location.get_name(),
                    "icon": self.location.icon,
                    "area": area.get_element_key(),
                    "pos": self.location.position
                }
            }

            exits = self.location.get_exits()

            for path in exits.values():
                # add room's neighbours
                neighbour_key = path["to"]
                if neighbour_key not in rooms:
                    try:
                        neighbour = Server.world.get_room(neighbour_key)
                        neighbour_area = Server.world.get_area_by_room(neighbour_key)
                        rooms[neighbour_key] = {
                            "name": neighbour.get_name(),
                            "icon": neighbour.icon,
                            "area": neighbour_area.get_element_key(),
                            "pos": neighbour.position
                        }
                    except ObjectDoesNotExist:
                        pass

            msg["reveal_map"] = {"rooms": rooms, "exits": exits}

        # get appearance
        appearance = self.location.get_appearance(self)
        appearance.update(self.location.get_surroundings(self))
        msg["look_around"] = appearance

        self.msg(msg)

    ################################################
    #
    # INVENTORY
    #   load_inventory: Load character's inventory from db and check default objects.
    #   total_object_number: get the object's number by key.
    #   has_object: Check the specified object in the inventory.
    #
    ################################################
    def load_inventory(self):
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
        inventory = CharacterInventory.get_character(self.get_db_id())
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
            self.receive_objects(obj_list, mute=True)

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

    def receive_object(self, object_key, number, level, mute=False):
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
        return self.receive_objects(obj_list, mute)

    def receive_objects(self, obj_list, mute=False, show=True):
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
        def add_new_object(object_key, level, number, element_type, can_remove):
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
            CharacterInventory.add(self.get_db_id(), new_position, object_key, number, level)

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
                add_new_object(object_key, level, number, object_record.element_type, object_record.can_remove)

            else:
                # common number
                if object_record.unique:
                    # unique object
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
                            CharacterInventory.set_dict(self.get_db_id(), item["position"], {"number": current_number + add})
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
                        add_new_object(object_key, level, add, object_record.element_type, object_record.can_remove)

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
                            CharacterInventory.set_dict(self.get_db_id(), item["position"], {"number": current_number + add})

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
                        add_new_object(object_key, level, add, object_record.element_type, object_record.can_remove)

                        number -= add
                        accepted += add

            objects.append({
                "key": object_record.key,
                "name": object_record.name,
                "icon": object_record.icon,
                "number": accepted,
                "reject": reject,
            })

        if not mute:
            # Send results to the player.
            self.msg({"get_objects": objects})

        if show:
            self.show_inventory()

        # call quest handler
        for item in objects:
            if not item["reject"]:
                self.quest_handler.at_objective(defines.OBJECTIVE_OBJECT, item["key"], item["number"])

        return objects

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

    def get_inventory_obj_by_pos(self, position):
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
            new_obj.setup_element(item["object_key"], item["level"])
            item["obj"] = new_obj
            return new_obj

    def get_inventory_obj_by_key(self, obj_key):
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
                    new_obj.setup_element(item["object_key"], item["level"])
                    item["obj"] = new_obj
                    return new_obj

        return None

    def use_object(self, position, number=1):
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
            return _("Not enough number.")

        item_obj = self.get_inventory_obj_by_pos(position)

        # take effect
        try:
            result, used = item_obj.take_effect(self, number)
            if used > 0:
                # remove used object
                self.remove_objects_by_position(position, used, True)

            self.show_inventory()
            return result
        except Exception as e:
            ostring = "Can not use %s: %s" % (item["key"], e)
            logger.log_tracemsg(ostring)

        return _("No effect.")

    def remove_all_objects_by_position(self, position, mute=False):
        """
        Remove all objects by its position.

        :param position:
        :param mute:
        :return:
        """
        if position not in self.inventory:
            raise MudderyError(_("Can not find this object."))

        item = self.inventory[position]
        if item["can_remove"]:
            CharacterInventory.remove_object(self.get_db_id(), position)
            del self.inventory[position]
        else:
            CharacterInventory.set_dict(self.get_db_id(), position, {"number": 0})
            item["number"] = 0

        if not mute:
            self.show_inventory()

        return

    def remove_objects_by_position(self, position, number, mute=False):
        """
        Remove objects by its position.

        :param obj_id:
        :param mute:
        :return:
        """
        if position not in self.inventory:
            raise MudderyError(_("Can not find this object."))

        if number <= 0:
            raise MudderyError(_("Can not remove by %s.") % number)

        item = self.inventory[position]
        obj_num = item["number"]
        if obj_num > number:
            CharacterInventory.set_dict(self.get_db_id(), position, {"number": obj_num - number})
            item["number"] = obj_num - number
        elif obj_num == number:
            if item["can_remove"]:
                CharacterInventory.remove_object(self.get_db_id(), position)
                del self.inventory[position]
            else:
                CharacterInventory.set_dict(self.get_db_id(), position, {"number": 0})
                item["number"] = 0
        else:
            raise (MudderyError(_("Can not remove this object.")))

        if not mute:
            self.show_inventory()

        return

    def remove_all_objects_by_key(self, obj_key, mute=False):
        """
        Remove all objects of this object_key.
        """
        to_remove = []
        for position, item in self.inventory.items():
            if item["object_key"] == obj_key:
                to_remove.append(position)

        for position in to_remove:
            if self.inventory[position]["can_remove"]:
                CharacterInventory.remove_object(self.get_db_id(), position)
                del self.inventory[position]
            else:
                CharacterInventory.set_dict(self.get_db_id(), position, {"number": 0})
                self.inventory[position]["number"] = 0

        if not mute:
            self.show_inventory()

        return

    def remove_objects_by_key(self, obj_key, number, mute=False):
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
                CharacterInventory.set_dict(self.get_db_id(), position, {"number": obj_num - number})
                item["number"] = obj_num - number
                number = 0
            else:
                number -= obj_num
                if item["can_remove"]:
                    CharacterInventory.remove_object(self.get_db_id(), position)
                    del self.inventory[position]
                else:
                    CharacterInventory.set_dict(self.get_db_id(), position, {"number": 0})
                    item["number"] = 0

            if number == 0:
                break

        if not mute:
            self.show_inventory()

        return

    def remove_objects_by_list(self, obj_list, mute=False, show=True):
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
            self.remove_objects_by_key(item["object_key"], item["number"], True)

        if show:
            self.show_inventory()

    def exchange_objects(self, remove_list, receive_list, mute=False, show=True):
        """
        Exchange some objects to other objects.

        :param remove_list:
        :param receive_list:
        :param mute:
        :return:
        """
        with self.states.atomic():
            self.remove_objects_by_list(remove_list, mute=True, show=False)
            self.receive_objects(receive_list, mute=True, show=False)

        if show:
            self.show_inventory()

    def show_inventory(self):
        """
        Send inventory data to player.
        """
        self.msg({"inventory": self.get_inventory_appearance()})

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

    def get_inventory_object_appearance(self, position):
        """
        Get inventory's data.
        """
        if position in self.inventory:
            item = self.inventory[position]
            item_obj = self.get_inventory_obj_by_pos(position)

            appearance = item_obj.get_appearance(self)
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

    def return_equipments_object(self, position):
        """
        Get equipments data.
        """
        if position in self.equipments:
            appearance = self.equipments[position]["obj"].get_appearance(self)

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

    def show_status(self):
        """
        Send status to player.
        """
        status = self.return_status()
        self.msg({
            "status": status
        })

    def return_status(self):
        """
        Get character's status.
        """
        status = {
            "level": {
                "name": _("LEVEL"),
                "value": self.get_level(),
            }
        }

        status.update({
            key: {
                "name": info["name"],
                "value": self.const_data_handler.get(key),
            } for key, info in self.get_properties_info().items()
        })

        records = CharacterStatesDict.all()
        status.update({
            record.key: {
                "name": record.name,
                "value": self.states.load(record.key)
            } for record in records
        })

        return status

    def load_equipments(self):
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
        self.equipments = CharacterEquipments.get_character(self.get_db_id())

        # get equipment's position
        positions = set([r.key for r in EquipmentPositions.all()])
        common_models = ELEMENT("POCKET_OBJECT").get_models()

        for pos in list(self.equipments.keys()):
            if pos in positions:
                # create an instance of the equipment
                item = self.equipments[pos]

                object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
                object_record = object_record[0]
                item["element_type"] = object_record.element_type

                new_obj = ELEMENT(item["element_type"])()
                new_obj.setup_element(item["object_key"], item["level"])
                item["obj"] = new_obj
            else:
                # the position has been removed, take off the equipment.
                self.take_off_equipment(pos, mute=True, refresh=False)

    def show_equipments(self):
        """
        Send equipments to player.
        """
        self.msg({
            "equipments": self.return_equipments()
        })

    def return_equipments(self):
        """
        Get equipments' data.
        """
        info = {}
        for pos, item in self.equipments.items():
            # order by positions
            obj = item["obj"]
            info[pos] = {
                "key": item["object_key"],
                "name": obj.get_name(),
                "desc": obj.get_desc(),
                "icon": obj.get_icon(),
            }

        return info

    def equip_object(self, position):
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
            self.take_off_equipment(body_position, mute=True, refresh=False)

        # Put on new equipment.
        if "obj" not in item or not item["obj"]:
            # create an instance of the equipment
            new_obj = ELEMENT(item["element_type"])()
            new_obj.setup_element(item["object_key"], item["level"])
            item["obj"] = new_obj

        CharacterEquipments.add(self.get_db_id(), body_position, item["object_key"], item["level"])
        self.equipments[body_position] = item

        # Remove from the inventory
        self.remove_objects_by_position(position, 1, True)

        # reset character's attributes
        self.refresh_states(True)

        message = {
            "status": self.return_status(),
            "equipments": self.return_equipments(),
            "inventory": self.get_inventory_appearance()
        }
        self.msg(message)

        return

    def take_off_equipment(self, body_position, mute=False, refresh=True):
        """
        Take off an equipment.
        args:
            position: (string) a position on the body.
        """
        if body_position not in self.equipments:
            raise MudderyError(_("Can not find this equipment."))

        item = self.equipments[body_position]
        self.receive_object(item["object_key"], 1, item["level"], True)
        CharacterEquipments.remove_equipment(self.get_db_id(), body_position)
        del self.equipments[body_position]

        if refresh:
            # reset character's attributes
            self.refresh_states(True)

        if not mute:
            message = {
                "status": self.return_status(),
                "equipments": self.return_equipments(),
                "inventory": self.get_inventory_appearance()
            }
            self.msg(message)

    def lock_exit(self, exit_key):
        """
        Lock an exit. Remove the exit's key from the character's unlock list.
        """
        unlocked_exits = self.states.load("unlocked_exits", set())
        if exit_key not in unlocked_exits:
            return

        unlocked_exits.remove(exit_key)
        self.states.save("unlocked_exits", unlocked_exits)

    def unlock_exit(self, exit_key):
        """
        Unlock an exit. Add the exit's key to the character's unlock list.
        """
        unlocked_exits = self.states.load("unlocked_exits", set())
        if exit_key in unlocked_exits:
            return True

        if not self.location.can_unlock_exit(self, exit_key):
            self.msg({"msg": _("Can not open this exit.")})
            return False

        unlocked_exits.add(exit_key)
        self.states.save("unlocked_exits", unlocked_exits)

        # The exit may have different appearance after unlocking.
        # Send the lastest appearance to the caller.
        appearance = self.location.get_exit_appearance(self, exit_key)
        self.msg({"look_obj": appearance})

        return True

    def is_exit_unlocked(self, exit_key):
        """
        Whether the exit is unlocked.
        """
        unlocked_exits = self.states.load("unlocked_exits", set())
        return exit_key in unlocked_exits

    def load_skills(self):
        """
        Load character's skills.
        """
        self.skills = {}

        # default skills
        default_skills = DefaultSkills.get(self.get_element_key())
        default_skill_set = set([r.skill for r in default_skills])

        # current skills
        character_skills = CharacterSkills.load_character(self.get_db_id())

        for key, item in character_skills.items():
            if item["is_default"]:
                if key not in default_skill_set:
                    # default skill is deleted, remove it from db
                    CharacterSkills.delete(self.get_db_id(), key)
                    continue

            try:
                # Create skill object.
                skill_obj = ELEMENT("SKILL")()
                skill_obj.setup_element(key, item["level"])
            except Exception as e:
                logger.log_err("Can not load skill %s: (%s) %s" % (key, type(e).__name__, e))
                continue

            # Store new skill.
            self.skills[key] = {
                "obj": skill_obj,
                "cd_finish": 0,
            }

        # add new default skills
        for item in default_skills:
            key = item.skill
            if key not in self.skills:
                try:
                    # Create skill object.
                    skill_obj = ELEMENT("SKILL")()
                    skill_obj.setup_element(key, item.level)
                except Exception as e:
                    logger.log_err("Can not load skill %s: (%s) %s" % (key, type(e).__name__, e))
                    continue

                # Store new skill.
                self.skills[key] = {
                    "obj": skill_obj,
                    "cd_finish": 0,
                }

                # save skill
                CharacterSkills.save(self.get_db_id(), key, {
                    "level": item.level,
                    "is_default": True,
                    "cd_finish": 0,
                })

    def learn_skill(self, skill_key, level, mute=True):
        """
        Learn a new skill.

        Args:
            skill_key: (string) skill's key
            level: (number) skill's level
            mute: (boolean) do not show messages to the player

        Returns:
            (boolean) learned skill
        """
        if skill_key in self.skills:
            self.msg({"msg": _("You have already learned this skill.")})
            raise KeyError

        try:
            # Create skill object.
            skill_obj = ELEMENT("SKILL")()
            skill_obj.setup_element(skill_key, level)
        except Exception as e:
            logger.log_err("Can not learn skill %s: (%s) %s" % (skill_key, type(e).__name__, e))
            self.msg({"msg": _("Can not learn this skill.")})
            raise e

        # Store new skill.
        self.skills[skill_key] = {
            "obj": skill_obj,
            "cd_finish": 0,
        }

        # save skill
        CharacterSkills.save(self.get_db_id(), skill_key, {
            "level": level,
            "is_default": False,
            "cd_finish": 0,
        })

        # If it is a passive skill, player's status may change.
        if skill_obj.passive:
            self.refresh_states(True)

        # Notify the player
        if not mute:
            self.show_status()
            self.show_skills()
            self.msg({"msg": _("You learned skill {C%s{n.") % skill_obj.get_name()})

        return

    def show_skills(self):
        """
        Send skills to player.
        """
        skills = self.return_skills()
        self.msg({"skills": skills})

    def return_skills(self):
        """
        Get skills' data.
        """
        skills_list = []

        for skill in self.skills.values():
            skills_list.append(skill["obj"].get_appearance(self))

        return skills_list

    def cast_passive_skills(self):
        """
        Cast all passive skills.
        """
        for skill in self.skills.values():
            if skill["obj"].is_passive():
                skill["obj"].cast(self, self)

    def cast_skill(self, skill_key, target):
        """
        Cast a skill.

        Args:
            skill_key: (string) skill's key.
            target: (object) skill's target.
        """
        if not self.skills[skill_key]["obj"].is_available(self, False):
            return

        last_cd_finish = self.skills[skill_key]["cd_finish"]
        result = super(MudderyPlayerCharacter, self).cast_skill(skill_key, target)
        cd_finish = self.skills[skill_key]["cd_finish"]

        if last_cd_finish != cd_finish:
            CharacterSkills.save(self.get_db_id(), skill_key, {"cd_finish": cd_finish})

        return result

    def close_event(self, event_key):
        """
        If an event is closed, it will never be triggered.

        Args:
            event_key: (string) event's key
        """
        # set closed events
        closed_events = self.states.load("closed_events", set())
        closed_events.add(event_key)
        self.states.save("closed_events", closed_events)

    def is_event_closed(self, event_key):
        """
        Return True If this event is closed.

        Args:
            event_key: (string) event's key
        """
        closed_events = self.states.load("closed_events", set())
        return event_key in closed_events

    def join_combat(self, combat_id):
        """
        The character joins a combat.

        :param combat_id: (int) combat's id.
        :return:
        """
        super(MudderyPlayerCharacter, self).join_combat(combat_id)
        CharacterCombat.save(self.get_db_id(), combat_id)

    def get_combat(self):
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
            CharacterCombat.remove_character(self.get_db_id())

        return combat

    def resume_combat(self):
        """
        Resume unfinished combat.

        Returns:
            None
        """
        combat = self.get_combat()
        if combat:
            if not combat.is_finished():
                # show combat infomation
                combat.show_combat(self)
            else:
                self.leave_combat()

    def combat_result(self, combat_type, result, opponents=None, rewards=None):
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
                self.add_exp(exp)
                combat_result["rewards"]["exp"] = exp

            # give objects to winner
            if "loots" in rewards and rewards["loots"]:
                get_objects = self.receive_objects(rewards["loots"], mute=True)
                combat_result["rewards"]["get_objects"] = get_objects

            # honours
            if "honour" in rewards and rewards["honour"]:
                combat_result["rewards"]["honour"] = rewards["honour"]

        self.msg({"combat_finish": combat_result})

    def leave_combat(self):
        """
        Leave the current combat.
        """
        status = None
        opponents = None
        rewards = None

        combat = self.get_combat()
        if not combat:
            return

        result = combat.get_combat_result(self.id)
        if result:
            status, opponents, rewards = result

        combat_type = combat.get_combat_type()

        if combat_type == CombatType.NORMAL:
            # normal combat
            # trigger events
            if status == defines.COMBAT_WIN:
                for opponent in opponents:
                    self.event.at_character_kill(opponent)

                # call quest handler
                for opponent in opponents:
                    self.quest_handler.at_objective(defines.OBJECTIVE_KILL, opponent.get_element_key())
            elif status == defines.COMBAT_LOSE:
                self.die(opponents)
                self.event.at_character_die()
        elif combat_type == CombatType.HONOUR:
            if status == defines.COMBAT_WIN:
                self.honour_win()
            elif status == defines.COMBAT_LOSE:
                self.honour_lose()

        combat.leave_combat(self)
        self.combat_id = None

        # show status
        self.show_status()

        self.show_location()

    def die(self, killers):
        """
        This character is killed. Move it to it's home.
        """

        # player's character can always reborn
        if self.reborn_time < 1:
            self.reborn_time = 1

        super(MudderyPlayerCharacter, self).die(killers)
        
        self.msg({"msg": _("You died.")})

        if self.reborn_time > 0:
            self.msg({"msg": _("You will be reborn in {C%(s)s{n seconds.") % {'s': self.reborn_time}})

    def honour_win(self):
        """
        The character win in an honour combat.
        """
        # Recover properties.
        self.recover()
        self.show_status()

    def honour_lose(self):
        """
        The character lost in an honour combat.
        """
        # Recover properties.
        self.recover()
        self.show_status()

    def reborn(self):
        """
        Reborn after being killed.
        """
        # Reborn at its home.
        home = None
        default_home_key = GAME_SETTINGS.get("default_player_home_key")
        if default_home_key:
            try:
                home = Server.world.get_room(default_home_key)
            except ObjectDoesNotExist:
                pass;

        if home:
            self.move_to(home)

        # Recover properties.
        self.recover()
        self.show_status()

        if home:
            self.msg({"msg": _("You are reborn at {C%s{n.") % home.get_name()})
        else:
            self.msg({"msg": _("You are reborn.")})

    def save_current_dialogues(self, current_dialogue):
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

        if not GAME_SETTINGS.get("auto_resume_dialogues"):
            # Can not auto resume dialogues.
            return

        self.states.save("current_dialogue", current_dialogue if current_dialogue else None)
        return

    def resume_last_dialogue(self):
        """
        Restore player's dialogues when he return to game.

        Returns:
            None
        """
        if not GAME_SETTINGS.get("auto_resume_dialogues"):
            # Can not auto resume dialogues.
            return

        current_dialogue = self.states.load("current_dialogue")
        if not current_dialogue:
            return

        self.msg({"dialogue": current_dialogue})
        return


    def talk_to_npc(self, npc):
        """
        Talk to an NPC.

        Args:
            npc: NPC's object.

        Returns:
            None
        """
        # Set caller's target.
        self.set_target(npc)

        # Get NPC's dialogue list.
        dialogues = DIALOGUE_HANDLER.get_npc_dialogues(self, npc)
        
        self.save_current_dialogues(dialogues)
        self.msg({"dialogue": dialogues})

    def show_dialogue(self, dlg_key):
        """
        Show a dialogue.

        Args:
            dlg_key: dialogue's key.

        Returns:
            None
        """
        # Get next sentences_list.
        dialogue = DIALOGUE_HANDLER.get_dialogues_by_key(dlg_key)

        # Send the dialogue to the player.
        self.save_current_dialogues(dialogue)
        self.msg({"dialogue": dialogue})

    def finish_dialogue(self, dlg_key, npc):
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

        try:
            # Finish current dialogue
            DIALOGUE_HANDLER.finish_dialogue(dlg_key, self, npc)
        except Exception as e:
            ostring = "Can not finish dialogue %s: %s" % (dlg_key, e)
            logger.log_tracemsg(ostring)

        # Get next dialogue.
        next_dialogues = DIALOGUE_HANDLER.get_next_dialogues(dlg_key, self, npc)

        # Send dialogues_list to the player.
        self.save_current_dialogues(next_dialogues)
        self.msg({"dialogue": next_dialogues})
        if not next_dialogues:
            # dialogue finished, refresh surroundings
            self.show_location()            

    def add_exp(self, exp):
        """
        Add character's exp.
        Args:
            exp: (number) the exp value to add.
        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).add_exp(exp)

        self.msg({"get_exp": {"exp": exp}})

    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).level_up()

        # notify the player
        self.msg({"msg": _("{C%s upgraded to level %s.{n") % (self.get_name(), self.get_level())})

    def get_message(self, caller, message):
        """
        Receive a message from a character.

        :param caller: talker.
        :param message: content.
        """
        output = {
            "type": ConversationType.PRIVATE.value,
            "channel": self.get_name(),
            "from_obj": caller.get_id(),
            "from_name": caller.get_name(),
            "msg": message
        }
        self.msg({"conversation": output})
        caller.msg({"conversation": output})

    def show_rankings(self):
        """
        Show character's rankings.
        """
        honour_settings = HonourSettings.get_first_data()
        top_rankings = HONOURS_MAPPER.get_top_rankings(honour_settings.top_rankings_number)
        nearest_rankings = HONOURS_MAPPER.get_nearest_rankings(self, honour_settings.nearest_rankings_number)

        rankings = top_rankings
        rankings.extend([char_id for char_id in nearest_rankings if char_id not in top_rankings])

        data = [{"name": CharacterInfo.get_nickname(char_id),
                 "id": char_id,
                 "ranking": HONOURS_MAPPER.get_ranking(char_id),
                 "honour": HONOURS_MAPPER.get_honour(char_id)} for char_id in rankings]
        self.msg({"rankings": data})

    def get_quest_info(self, quest_key):
        """
        Get a quest's detail information.
        :param quest_key:
        :return:
        """
        return self.quest_handler.get_quest_info(quest_key)

    def get_skill_info(self, skill_key):
        """
        Get a skill's detail information.
        :param skill_key:
        :return:
        """
        return self.skills[skill_key]["obj"].get_appearance(self)

    def at_cmdset_get(self, **kwargs):
        """
        Called just before cmdsets on this object are requested by the
        command handler. If changes need to be done on the fly to the
        cmdset before passing them on to the cmdhandler, this is the
        place to do it. This is called also if the object currently
        have no cmdsets.

        Kwargs:
            caller (Session, Object or Account): The caller requesting
                this cmdset.

        """
        pass

    @lazy_property
    def cmdset(self):
        return CmdSetHandler(self, True)

    @lazy_property
    def scripts(self):
        return ScriptHandler(self)
