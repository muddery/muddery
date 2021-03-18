"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import ast
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils.utils import lazy_property
from evennia.utils import logger
from evennia.comms.models import ChannelDB
from evennia.objects.models import ObjectDB
from muddery.server.utils import search
from muddery.server.utils.builder import build_object
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
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils import defines
from muddery.server.utils.data_field_handler import DataFieldHandler, ConstDataHolder
from muddery.server.database.gamedata.honours_mapper import HONOURS_MAPPER
from muddery.server.database.gamedata.character_inventory import CHARACTER_INVENTORY_DATA
from muddery.server.database.gamedata.player_character import PLAYER_CHARACTER_DATA
from muddery.server.database.gamedata.character_skills import CHARACTER_SKILLS
from muddery.server.database.worlddata.object_properties import ObjectProperties
from muddery.server.database.worlddata.equipment_positions import EquipmentPositions
from muddery.server.combat.match_pvp_handler import MATCH_COMBAT_HANDLER


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

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyPlayerCharacter, self).at_object_creation()

        PLAYER_CHARACTER_DATA.add(self.id)

    def after_creation(self):
        """
        Called once, after the object is created by Muddery.
        """
        super(MudderyPlayerCharacter, self).after_creation()

        # refresh the character's properties.
        self.refresh_properties(False)

    def at_object_delete(self):
        """
        Called just before the database object is permanently
        delete()d from the database. If this method returns False,
        deletion is aborted.
        """
        result = super(MudderyPlayerCharacter, self).at_object_delete()
        if not result:
            return result

        # delete inventory objects
        CHARACTER_INVENTORY_DATA.remove_character(self.id)

        # delete equipments
        for pos, item in self.equipments.items():
            item["obj"].delete()

        # remove the character's honour
        HONOURS_MAPPER.remove_honour(self.id)

        # remove the character's data
        PLAYER_CHARACTER_DATA.remove(self.id)

        # remove quests
        self.quest_handler.remove_all()

        return True

    def after_data_loaded(self):
        """
        """
        super(MudderyPlayerCharacter, self).after_data_loaded()

        self.solo_mode = GAME_SETTINGS.get("solo_mode")
        self.available_channels = {}
        self.current_dialogues = set()

        # load inventory
        self.load_inventory()

        # load equipments
        self.load_equipments()

        # refresh data
        self.refresh_properties(True)

        # if it is dead, reborn at init.
        if not self.is_alive():
            if not self.is_temp and self.reborn_time > 0:
                self.reborn()

    def load_custom_data(self, level):
        """
        Load body properties from db. Body properties do no include mutable properties.
        """
        # Get object level.
        if level is None:
            level = self.get_level()

        # Load values from db.
        object_key = self.const.clone if self.const.clone else self.get_object_key()

        values = {}
        for record in ObjectProperties.get_properties(object_key, level):
            key = record.property
            serializable_value = record.value
            if serializable_value == "":
                value = None
            else:
                try:
                    value = ast.literal_eval(serializable_value)
                except (SyntaxError, ValueError) as e:
                    # treat as a raw string
                    value = serializable_value
            values[key] = value

        # Set body values.
        for key, info in self.get_properties_info().items():
            if not info["mutable"]:
                self.const_data_handler.add(key, values.get(key, ast.literal_eval(info["default"])))
                self.body_data_handler.add(key, values.get(key, ast.literal_eval(info["default"])))
            else:
                # Set default mutable properties to prop.
                if not self.states.has(key):
                    self.states.save(key, self.get_custom_data_value(info["default"]))

    def move_to(self, destination, quiet=False,
                emit_to_obj=None, use_destination=True, to_none=False, move_hooks=True, **kwargs):
        """
        Moves this object to a new location.
        """
        if not quiet and self.solo_mode:
            # If in solo mode, move quietly.
            quiet = True

        return super(MudderyPlayerCharacter, self).move_to(destination,
                                                           quiet,
                                                           emit_to_obj,
                                                           use_destination,
                                                           to_none,
                                                           move_hooks)

    def at_before_move(self, destination, **kwargs):
        """
        Called just before starting to move this object to
        destination.
        """
        # trigger event
        if self.has_account:
            self.location.event.at_character_move_out(self)

        return True

    def at_after_move(self, source_location):
        """
        We make sure to look around after a move.

        """
        self.msg({"msg": _("Moved to %s ...") % self.location.name})
        self.show_location()

        # trigger event
        if self.has_account:
            self.location.event.at_character_move_in(self)
            self.quest_handler.at_objective(defines.OBJECTIVE_ARRIVE, self.location.get_object_key())

    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        self.available_channels = self.get_available_channels()

        allow_commands = False
        if self.account:
            if self.is_superuser:
                allow_commands = True
            else:
                for perm in self.account.permissions.all():
                    if perm in settings.PERMISSION_COMMANDS:
                        allow_commands = True
                        break

        # Django's superuser even it is quelled.
        if not allow_commands:
            allow_commands = self.db_account and self.db_account.is_superuser

        # Send puppet info to the client first.
        output = {
            "id": self.get_id(),
            "name": self.get_name(),
            "icon": getattr(self, "icon", None),
        }

        if allow_commands:
            output["allow_commands"] = True

        self.msg({"puppet": output})

        # send character's data to player
        message = {
            "status": self.return_status(),
            "equipments": self.return_equipments(),
            "inventory": self.return_inventory(),
            "skills": self.return_skills(),
            "quests": self.quest_handler.return_quests(),
            "revealed_map": self.get_revealed_map(),
            "channels": self.available_channels
        }
        self.msg(message)

        self.show_location()

        # notify its location
        if not self.solo_mode:
            if self.location:
                change = {"id": self.get_id(),
                          "name": self.get_name()}
                self.location.msg_contents({"player_online": change}, exclude=[self])

        self.resume_last_dialogue()

        self.resume_combat()

        # Resume all scripts.
        scripts = self.scripts.all()
        for script in scripts:
            script.unpause()

    def at_pre_unpuppet(self):
        """
        Called just before beginning to un-connect a puppeting from
        this Player.
        """
        # Pause all scripts.
        scripts = self.scripts.all()
        for script in scripts:
            script.pause()

        if not self.solo_mode:
            # notify its location
            if self.location:
                change = {"id": self.get_id(),
                          "name": self.get_name()}
                self.location.msg_contents({"player_offline":change}, exclude=self)

        MATCH_COMBAT_HANDLER.remove(self)

    def refresh_properties(self, keep_values):
        """
        Refresh character's final properties.

        Args:
            keep_values (boolean): mutable values keep last values.
        """
        if keep_values:
            last_properties = self.states.all()

        # Load body properties.
        for key, value in self.body_data_handler.all().items():
            self.const_data_handler.add(key, value)

        # load equips
        self.wear_equipments()

        # load passive skills
        self.cast_passive_skills()

        if keep_values:
            for key, info in self.get_properties_info().items():
                if info["mutable"]:
                    value = last_properties[key]

                    # check limits
                    max_key = "max_" + key
                    if self.const_data_handler.has(max_key):
                        max_value = self.const_data_handler.get(max_key)
                        if value > max_value:
                            value = max_value

                    min_key = "min_" + key
                    if self.const_data_handler.has(min_key):
                        min_value = self.const_data_handler.get(min_key)
                        if value < min_value:
                            value = min_value

                    # Set the value.
                    self.const_data_handler.add(key, value)

    def get_object_key(self):
        """
        Get the object's key.
        """
        if not hasattr(self, "object_key"):
            self.object_key = GAME_SETTINGS.get("default_player_character_key")

        return self.object_key

    def set_nickname(self, nickname):
        """
        Set player character's nickname.
        """
        PLAYER_CHARACTER_DATA.update_nickname(self.id, nickname)

    def get_name(self):
        """
        Get player character's name.
        """
        # Use nick name instead of normal name.
        return PLAYER_CHARACTER_DATA.get_nickname(self.id)

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

        """
        commands = False
        if self.account:
            if self.is_superuser:
                commands = True
            else:
                for perm in self.account.permissions.all():
                    if perm in settings.PERMISSION_COMMANDS:
                        commands = True
                        break

        # Django's superuser even it is quelled.
        if not commands:
            commands = self.db_account and self.db_account.is_superuser

        if commands:
            channels["CMD"] = {
                "type": "CMD",
                "name": _("Cmd"),
            }
        """
        return channels

    def set_level(self, level):
        """
        Set object's level.
        Args:
            level: object's new level

        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).set_level(level)

        self.refresh_properties(False)

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
                room = search.get_object_by_key(room_key)
                rooms[room_key] = {"name": room.get_name(),
                                   "icon": room.icon,
                                   "area": room.location and room.location.get_object_key(),
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
                    neighbour = search.get_object_by_key(path["to"])
                    rooms[neighbour.get_object_key()] = {
                        "name": neighbour.get_name(),
                        "icon": neighbour.icon,
                        "area": neighbour.location and neighbour.location.get_object_key(),
                        "pos": neighbour.position
                    }
                except ObjectDoesNotExist:
                    pass

        return {"rooms": rooms, "exits": exits}

    def total_object_number(self, obj_key):
        """
        Search specified object in the inventory.
        """
        objects = [item["number"] for item in self.inventory if item["object_key"] == obj_key]
        total = sum(objects)
        for item in self.equipments.values():
            if item["key"] == obj_key:
                total += 1

        return total

    def has_object(self, obj_key):
        """
        Check specified object in the inventory.
        """
        return self.total_object_number(obj_key) > 0

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
        if self.location:
            location_key = self.location.get_object_key()
            area = self.location.location and self.location.location.get_appearance(self)

            msg = {"current_location": {"key": location_key,
                                        "area": area}}

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
                revealed_map.add(self.location.get_object_key())
                self.states.save("revealed_map", revealed_map)

                rooms = {
                    location_key: {
                        "name": self.location.get_name(),
                        "icon": self.location.icon,
                        "area": self.location.location and self.location.location.get_object_key(),
                        "pos": self.location.position
                    }
                }

                exits = self.location.get_exits()

                for path in exits.values():
                    # add room's neighbours
                    if not path["to"] in rooms:
                        try:
                            neighbour = search.get_object_by_key(path["to"])
                            rooms[neighbour.get_object_key()] = {
                                "name": neighbour.get_name(),
                                "icon": neighbour.icon,
                                "area": neighbour.location and neighbour.location.get_object_key(),
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

    def load_inventory(self):
        """
        Load character's default objects.
        """
        inventory = CHARACTER_INVENTORY_DATA.get_character(self.id)
        self.inventory = [{"position": pos, **inventory[pos]} for pos in sorted(inventory)]

        # default objects
        object_records = DefaultObjects.get(self.get_object_key())

        # add new default objects
        obj_list = []
        for object_record in object_records:
            found = False
            for item in self.inventory:
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

    def receive_objects(self, obj_list, mute=False):
        """
        Add objects to the inventory.

        Args:
            obj_list: (list) a list of object keys and there numbers.
                             list item: {"object_key": object's key
                                         "number": object's number}
            mute: (boolean) do not send messages to the owner

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
        objects = []           # objects that have been accepted

        for obj in obj_list:
            object_key = obj["object_key"]
            level = obj.get("level", None)
            available = obj["number"]
            number = available
            accepted = 0
            reject = False

            try:
                common_models = ELEMENT("COMMON_OBJECT").get_models()
                object_record = WorldData.get_tables_data(common_models, key=object_key)
                object_record = object_record[0]
            except Exception as e:
                logger.log_err("Can not find object %s: %s" % (object_key, e))
                continue

            inventory_obj_list = [index for index, item in enumerate(self.inventory) if item["object_key"] == object_key]

            if number == 0:
                # it is an empty object
                if len(inventory_obj_list) > 0:
                    # already has this object
                    continue

                if object_record.can_remove:
                    # remove this empty object
                    continue

                # add a new content
                if len(self.inventory) > 0:
                    position = self.inventory[-1]["position"] + 1
                else:
                    position = 1

                new_obj = {
                    "position": position,
                    "object_key": object_key,
                    "number": number,
                    "level": level,
                }
                self.inventory.append(new_obj)
                CHARACTER_INVENTORY_DATA.add(self.id, position, object_key, number, level)
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
                            CHARACTER_INVENTORY_DATA.set_dict(self.id, item["position"], {"number": current_number + add})
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
                        if len(self.inventory) > 0:
                            position = self.inventory[-1]["position"] + 1
                        else:
                            position = 1

                        new_obj = {
                            "position": position,
                            "object_key": object_key,
                            "number": add,
                            "level": level,
                        }
                        self.inventory.append(new_obj)
                        CHARACTER_INVENTORY_DATA.add(self.id, position, object_key, add, level)

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
                            CHARACTER_INVENTORY_DATA.set_dict(self.id, item["position"], {"number": current_number + add})

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
                        if len(self.inventory) > 0:
                            position = self.inventory[-1]["position"] + 1
                        else:
                            position = 1

                        new_obj = {
                            "position": position,
                            "object_key": object_key,
                            "number": add,
                            "level": level,
                        }
                        self.inventory.append(new_obj)
                        CHARACTER_INVENTORY_DATA.add(self.id, position, object_key, add, level)

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
            message = {"get_objects": objects}
            self.msg(message)

        self.show_inventory()

        # call quest handler
        for item in objects:
            if not item["reject"]:
                self.quest_handler.at_objective(defines.OBJECTIVE_OBJECT, item["key"], item["number"])

        return objects

    def save_equipments(self):
        """
        Save equipments's data to db.
        :return:
        """
        self.states.save("equipments", {
            pos: {
                "key": item["key"],
                "id": item["id"],
            } for pos, item in self.equipments.items()
        })

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
            common_models = ELEMENT("COMMON_OBJECT").get_models()
            object_record = WorldData.get_tables_data(common_models, key=obj_key)
            object_record = object_record[0]
        except Exception as e:
            return False

        total = sum([item["number"] for item in self.inventory if obj_key == item["object_key"]])
        if not total:
            return True

        if not object_record.unique:
            return True

        if total + number <= object_record.max_stack:
            return True

        return False

    def use_object(self, position, number=1):
        """
        Use an object.

        Args:
            position: (int) object's position in the inventory
            number: (int) number to use

        Returns:
            result: (string) the description of the result
        """
        item = None
        for value in self.inventory:
            if value["position"] == position:
                item = value
                break
        if not item:
            raise MudderyError(_("Can not find this object."))

        if item["number"] < number:
            return _("Not enough number.")

        # take effect
        try:
            if "obj" not in item or not item["obj"]:
                new_obj = ELEMENT("COMMON_OBJECT")()
                new_obj.set_element_key(item["object_key"], item["level"])
                item["obj"] = new_obj

            result, used = item["obj"].take_effect(self, number)
            if used > 0:
                # remove used object
                self.remove_object_by_position(position, used, True)

            self.show_inventory()
            return result
        except Exception as e:
            ostring = "Can not use %s: %s" % (item["key"], e)
            logger.log_tracemsg(ostring)

        return _("No effect.")

    def remove_object_position_all(self, position, mute=False):
        """
        Remove an object by its id.

        :param position:
        :param mute:
        :return:
        """
        for index, item in enumerate(self.inventory):
            if item["position"] == position:
                common_models = ELEMENT("COMMON_OBJECT").get_models()
                object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
                object_record = object_record[0]

                if object_record.can_remove:
                    CHARACTER_INVENTORY_DATA.remove_object(self.id, position)
                    del self.inventory[index]
                else:
                    CHARACTER_INVENTORY_DATA.set_dict(self.id, position, {"number": 0})
                    item["number"] = 0

                if not mute:
                    self.show_inventory()

                return

        raise(MudderyError(_("Can not remove this object.")))

    def remove_object_by_position(self, position, number, mute=False):
        """
        Remove an object by its id.

        :param obj_id:
        :param mute:
        :return:
        """
        for index, item in enumerate(self.inventory):
            if item["position"] == position:
                obj_num = item["number"]
                if obj_num > 0:
                    if obj_num > number:
                        CHARACTER_INVENTORY_DATA.set_dict(self.id, position, {"number": obj_num - number})
                        item["number"] = obj_num - number
                    else:
                        common_models = ELEMENT("COMMON_OBJECT").get_models()
                        object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
                        object_record = object_record[0]

                        if object_record.can_remove:
                            CHARACTER_INVENTORY_DATA.remove_object(self.id, position)
                            del self.inventory[index]
                        else:
                            CHARACTER_INVENTORY_DATA.set_dict(self.id, position, {"number": 0})
                            item["number"] = 0

                    if not mute:
                        self.show_inventory()

                return

        raise(MudderyError(_("Can not remove this object.")))

    def remove_objects(self, obj_list, mute=False):
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
            self.remove_object(item["object_key"], item["number"], True)

        if not mute:
            self.show_inventory()

    def remove_object(self, obj_key, number, mute=False):
        """
        Remove objects from the inventory.

        Args:
            obj_key: object's key
            number: object's number
            mute: send inventory information

        Returns:
            boolean: success
        """
        # Count objects in the inventory.
        total = sum([item["number"] for item in self.inventory if obj_key == item["object_key"]])
        if total < number:
            raise (MudderyError(_("Can not remove this object.")))

        # remove objects
        to_remove = number
        try:
            index = 0
            while index < len(self.inventory):
                item = self.inventory[index]
                if item["object_key"] != obj_key:
                    index += 1
                    continue

                deleted = False
                obj_num = item["number"]
                if obj_num > 0:
                    if obj_num > to_remove:
                        # Reduce the object's number.
                        CHARACTER_INVENTORY_DATA.set_dict(self.id, item["position"], {"number": obj_num - to_remove})
                        item["number"] = obj_num - to_remove
                        to_remove = 0
                    else:
                        # Remove this object.
                        common_models = ELEMENT("COMMON_OBJECT").get_models()
                        object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
                        object_record = object_record[0]

                        if object_record.can_remove:
                            CHARACTER_INVENTORY_DATA.remove_object(self.id, item["position"])
                            del self.inventory[index]
                        else:
                            CHARACTER_INVENTORY_DATA.set_dict(self.id, item["position"], {"number": 0})
                            item["number"] = 0

                        to_remove -= obj_num
                        deleted = True

                if to_remove == 0:
                    break

                if not deleted:
                    index += 1

        except Exception as e:
            logger.log_tracemsg("Can not remove object %s: %s" % (obj_key, e))
            raise (MudderyError(_("Can not remove this object.")))

        if to_remove > 0:
            logger.log_err("Remove object error: %s" % obj_key)
            raise (MudderyError(_("Can not remove this object.")))

        if not mute:
            self.show_inventory()

    def exchange_objects(self, remove_list, receive_list, mute=False):
        """
        Exchange some objects to other objects.

        :param remove_list:
        :param receive_list:
        :param mute:
        :return:
        """
        with self.states.atomic():
            self.remove_objects(remove_list, True)
            self.receive_objects(receive_list, True)

        if not mute:
            self.show_inventory()

    def show_inventory(self):
        """
        Send inventory data to player.
        """
        self.msg({"inventory": self.return_inventory()})

    def return_inventory(self):
        """
        Get inventory's data.
        """
        inv = []

        common_models = ELEMENT("COMMON_OBJECT").get_models()
        for item in self.inventory:
            object_record = WorldData.get_tables_data(common_models, key=item["object_key"])
            object_record = object_record[0]
            info = {
                "position": item["position"],      # item's position
                "number": item["number"],           # item's number
                "name": object_record.name,             # item's name
                "desc": object_record.desc,         # item's desc
                "can_remove": object_record.can_remove,
                "icon": object_record.icon,             # item's icon
            }
            inv.append(info)

        # sort by created time
        # inv.sort(key=lambda x: x["id"])

        return inv

    def return_inventory_object(self, position):
        """
        Get inventory's data.
        """
        for item in self.inventory:
            if item["position"] == position:
                if "obj" not in item or not item["obj"]:
                    new_obj = ELEMENT("COMMON_OBJECT")()
                    new_obj.set_element_key(item["object_key"], item["level"])
                    item["obj"] = new_obj

                appearance = item["obj"].get_appearance(self)
                appearance["number"] = item["number"]

                # add a discard command
                if item["obj"].can_discard():
                    appearance["cmds"].append({
                        "name": _("Discard"),
                        "cmd": "discard",
                        "confirm": _("Discard this object?"),
                        "args": {
                            "position": position
                        }
                    })
                return appearance

    def return_equipments_object(self, obj_id):
        """
        Get equipments data.
        """
        for pos, item in self.equipments.items():
            if item["id"] == obj_id:
                appearance = item["obj"].get_appearance(self)

                appearance["number"] = item["number"]

                commands = [c for c in appearance["cmds"] if c["cmd"] != "equip" and c["cmd"] != "discard"]
                commands.append({
                    "name": _("Take Off"),
                    "cmd": "takeoff",
                    "args": obj_id,
                })
                appearance["cmds"] = commands

                return appearance

    def show_status(self):
        """
        Send status to player.
        """
        status = self.return_status()
        self.msg({"status": status})

    def return_status(self):
        """
        Get character's status.
        """
        status = {}
        status["level"] = {"name": _("LEVEL"),
                           "value": self.get_level()}

        for key, info in self.get_properties_info().items():
            if not info["mutable"]:
                status[key] = {"name": info["name"],
                               "value": self.const_data_handler.get(key)}
            else:
                status[key] = {"name": info["name"],
                               "value": self.states.load(key)}

        return status

    def load_equipments(self):
        """
        Reset equipment's position data.
        Returns:
            None
        """
        self.equipments = self.states.load("equipments", {})
        for pos, item in self.equipments.items():
            item["obj"] = ObjectDB.objects.get(id=item["id"])

        # get equipment's position
        positions = set([r.key for r in EquipmentPositions.all()])

        changed = False
        for pos in list(self.equipments.keys()):
            if pos not in positions:
                item = self.equipments[pos]
                item["number"] = 1
                self.inventory.append(item)
                del self.equipments[pos]
                changed = True

        if changed:
            # Save changes.
            with self.states.atomic():
                self.save_inventory()
                self.save_equipments()

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
            # in order of positions
            if item:
                obj = item["obj"]
                info[pos] = {
                    "id": item["id"],
                    "name": obj.get_name(),
                    "desc": obj.get_desc(self),
                    "icon": obj.get_icon(),
                }

        return info

    def equip_object(self, obj_id):
        """
        Equip an object.
        args: obj_id(int): the equipment object's id.
        """
        index = None
        item = None
        for i, value in enumerate(self.inventory):
            if value["id"] == obj_id:
                index = i
                item = value
                break

        if index is None:
            raise MudderyError(_("Can not find this equipment."))

        pos = item["obj"].position
        available_positions = set([r.key for r in EquipmentPositions.all()])
        if pos not in available_positions:
            raise MudderyError(_("Can not equip it on this position."))

        # Take off old equipment
        if pos in self.equipments and self.equipments[pos]:
            item = self.equipments[pos]
            item["number"] = 1
            self.inventory.append(item)
            self.equipments[pos] = None

        # Put on new equipment.
        self.equipments[pos] = item
        del self.inventory[index]

        # Save changes.
        with self.states.atomic():
            self.save_equipments()
            self.save_inventory()

        # reset character's attributes
        self.refresh_properties(True)

        message = {
            "status": self.return_status(),
            "equipments": self.return_equipments(),
            "inventory": self.return_inventory()
        }
        self.msg(message)

        return

    def take_off_equipment(self, obj_id):
        """
        Take off an equipment.
        args: obj_id(int): the equipment object's id.
        """
        pos = None
        item = None
        for key, value in self.equipments.items():
            if value["id"] == obj_id:
                pos = key
                item = value
                item["number"] = 1
                break

        if pos is None:
            raise MudderyError(_("Can not find this equipment."))

        self.inventory.append(item)
        del self.equipments[pos]

        # Save changes.
        with self.states.atomic():
            self.states.save("equipments", self.equipments)
            self.save_inventory()

        # reset character's attributes
        self.refresh_properties(True)

        message = {
            "status": self.return_status(),
            "equipments": self.return_equipments(),
            "inventory": self.return_inventory()
        }
        self.msg(message)

    def lock_exit(self, exit):
        """
        Lock an exit. Remove the exit's key from the character's unlock list.
        """
        exit_key = exit.get_object_key()
        unlocked_exits = self.states.load("unlocked_exits", set())
        if exit_key not in unlocked_exits:
            return

        unlocked_exits.remove(exit_key)
        self.states.save("unlocked_exits", unlocked_exits)

    def unlock_exit(self, exit):
        """
        Unlock an exit. Add the exit's key to the character's unlock list.
        """
        if exit.location != self.location:
            return False

        exit_key = exit.get_object_key()
        unlocked_exits = self.states.load("unlocked_exits", set())
        if exit_key in unlocked_exits:
            return True

        if not exit.can_unlock(self):
            self.msg({"msg": _("Can not open this exit.")})
            return False

        unlocked_exits.add(exit_key)
        self.states.save("unlocked_exits", unlocked_exits)
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
        default_skills = DefaultSkills.get(self.get_object_key())
        default_skill_set = set([r.skill for r in default_skills])

        # current skills
        character_skills = CHARACTER_SKILLS.load_character(self.id)

        for key, item in character_skills.items():
            if item["is_default"]:
                if key not in default_skill_set:
                    # default skill is deleted, remove it from db
                    CHARACTER_SKILLS.delete(self.id, key)
                    continue

            try:
                # Create skill object.
                skill_obj = ELEMENT("SKILL")()
                skill_obj.set_element_key(key, item["level"])
            except Exception as e:
                logger.log_err("Can not load skill %s: (%s) %s" % (key, type(e), e))
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
                    skill_obj.set_element_key(key, item.level)
                except Exception as e:
                    logger.log_err("Can not load skill %s: (%s) %s" % (key, type(e), e))
                    continue

                # Store new skill.
                self.skills[key] = {
                    "obj": skill_obj,
                    "cd_finish": 0,
                }

                # save skill
                CHARACTER_SKILLS.save(self.id, key, {
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
            skill_obj.set_element_key(skill_key, level)
        except Exception as e:
            logger.log_err("Can not learn skill %s: (%s) %s" % (skill_key, type(e), e))
            self.msg({"msg": _("Can not learn this skill.")})
            raise e

        # Store new skill.
        self.skills[skill_key] = {
            "obj": skill_obj,
            "cd_finish": 0,
        }

        # save skill
        CHARACTER_SKILLS.save(self.id, skill_key, {
            "level": level,
            "is_default": False,
            "cd_finish": 0,
        })

        # If it is a passive skill, player's status may change.
        if skill_obj.passive:
            self.refresh_properties(True)

        # Notify the player
        if not mute and self.has_account:
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
            CHARACTER_SKILLS.save(self.id, skill_key, {"cd_finish": cd_finish})

        return result

    def resume_combat(self):
        """
        Resume unfinished combat.

        Returns:
            None
        """
        combat_handler = getattr(self.ndb, "combat_handler", None)
        if combat_handler:
            if not combat_handler.is_finished():
                # show combat infomation
                combat_handler.show_combat(self)
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
        if self.ndb.combat_handler:
            result = self.ndb.combat_handler.get_combat_result(self.id)
            if result:
                status, opponents, rewards = result

        combat_type = self.ndb.combat_handler.get_combat_type()

        if combat_type == CombatType.NORMAL:
            # normal combat
            # trigger events
            if status == defines.COMBAT_WIN:
                for opponent in opponents:
                    opponent.event.at_character_kill(self)
                    opponent.event.at_character_die()

                # call quest handler
                for opponent in opponents:
                    self.quest_handler.at_objective(defines.OBJECTIVE_KILL, opponent.get_object_key())
            elif status == defines.COMBAT_LOSE:
                self.die(opponents)
        elif combat_type == CombatType.HONOUR:
            if status == defines.COMBAT_WIN:
                self.honour_win()
            elif status == defines.COMBAT_LOSE:
                self.honour_lose()

        # remove combat commands
        self.cmdset.delete(settings.CMDSET_COMBAT)

        if self.ndb.combat_handler:
            self.ndb.combat_handler.leave_combat(self)
            del self.ndb.combat_handler

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
                home = search.get_object_by_key(default_home_key)
            except ObjectDoesNotExist:
                pass;

        if not home:
            rooms = search.search_object(settings.DEFAULT_HOME)
            if rooms:
                home = rooms[0]

        if home:
            self.move_to(home, quiet=True)

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

    def show_dialogue(self, dlg_key, npc):
        """
        Show a dialogue.

        Args:
            dlg_key: dialogue's key.
            npc: (optional) NPC's object.

        Returns:
            None
        """
        # Get next sentences_list.
        dialogue = DIALOGUE_HANDLER.get_dialogues_by_key(dlg_key, npc)

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

        characters = [search.get_object_by_id(char_id) for char_id in rankings]
        data = [{"name": char.get_name(),
                 "id": char.get_id(),
                 "ranking": HONOURS_MAPPER.get_ranking(char),
                 "honour": HONOURS_MAPPER.get_honour(char)} for char in characters if char]
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
