"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import traceback
import random
from django.conf import settings
from django.apps import apps
from muddery.typeclasses.characters import MudderyCharacter
from muddery.typeclasses.common_objects import MudderyEquipment
from muddery.utils import defines, utils
from muddery.utils.builder import build_object, get_object_record
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from muddery.utils.quest_handler import QuestHandler
from muddery.utils.statement_attribute_handler import StatementAttributeHandler
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.worlddata.data_sets import DATA_SETS
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO
from evennia.utils.utils import lazy_property
from evennia.utils import logger
from evennia.comms.models import ChannelDB
from evennia import TICKER_HANDLER


class MudderyPlayerCharacter(MudderyCharacter):
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

    # initialize all handlers in a lazy fashion
    @lazy_property
    def quest_handler(self):
        return QuestHandler(self)

    # attributes used in statements
    @lazy_property
    def statement_attr(self):
        return StatementAttributeHandler(self)

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyPlayerCharacter, self).at_object_creation()

        # Set default data.
        if not self.attributes.has("nickname"):
            self.db.nickname = ""
        if not self.attributes.has("unlocked_exits"):
            self.db.unlocked_exits = set()
        if not self.attributes.has("revealed_map"):
            self.db.revealed_map = set()

        # set custom attributes
        if not self.attributes.has("attributes"):
            self.db.attributes = {}

        # Choose a random career.
        if not self.attributes.has("career"):
            self.db.career = ""
            try:
                careers = DATA_SETS.character_careers.objects.all()
                if careers:
                    career = random.choice(careers)
                    self.db.career = career.key
            except Exception, e:
                pass
        
    def after_data_loaded(self):
        """
        """
        super(MudderyPlayerCharacter, self).after_data_loaded()

        self.solo_mode = GAME_SETTINGS.get("solo_mode")

        self.available_channels = {}

        # refresh data
        self.refresh_data()

    def move_to(self, destination, quiet=False,
                emit_to_obj=None, use_destination=True, to_none=False, move_hooks=True):
        """
        Moves this object to a new location.
        """
        if (not quiet) and self.solo_mode:
            # If in solo mode, move quietly.
            quiet = True

        return super(MudderyPlayerCharacter, self).move_to(destination,
                                                           quiet,
                                                           emit_to_obj,
                                                           use_destination,
                                                           to_none,
                                                           move_hooks)

    def at_object_receive(self, moved_obj, source_location):
        """
        Called after an object has been moved into this object.
        
        Args:
        moved_obj (Object): The object moved into this one
        source_location (Object): Where `moved_object` came from.
        
        """
        super(MudderyPlayerCharacter, self).at_object_receive(moved_obj, source_location)

        # send latest inventory data to player
        self.msg({"inventory": self.return_inventory()})
    
    def at_object_left(self, moved_obj, target_location):
        """
        Called after an object has been removed from this object.
        
        Args:
        moved_obj (Object): The object leaving
        target_location (Object): Where `moved_obj` is going.
        
        """
        super(MudderyPlayerCharacter, self).at_object_left(moved_obj, target_location)
        
        # send latest inventory data to player
        self.msg({"inventory": self.return_inventory()})

    def at_after_move(self, source_location):
        """
        We make sure to look around after a move.

        """
        self.msg({"msg": _("Moving to %s ...") % self.location.name})
        self.show_location()

    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        self.available_channels = self.get_available_channels()
        
        # Send puppet info to the client first.
        self.msg({"puppet": {"dbref": self.dbref,
                             "name": self.get_name(),
                             "icon": getattr(self, "icon", None)}})

        # send character's data to player
        message = {"status": self.return_status(),
                   "equipments": self.return_equipments(),
                   "inventory": self.return_inventory(),
                   "skills": self.return_skills(),
                   "quests": self.quest_handler.return_quests(),
                   "revealed_map": self.get_revealed_map(),
                   "channels": self.available_channels}
        self.msg(message)

        self.show_location()

        # notify its location
        if not self.solo_mode:
            if self.location:
                change = {"dbref": self.dbref,
                          "name": self.get_name()}
                self.location.msg_contents({"player_online": change}, exclude=[self])

        self.resume_last_dialogue()

        self.resume_combat()

    def at_pre_unpuppet(self):
        """
        Called just before beginning to un-connect a puppeting from
        this Player.
        
        """
        if not self.solo_mode:
            # notify its location
            if self.location:
                change = {"dbref": self.dbref,
                          "name": self.get_name()}
                self.location.msg_contents({"player_offline":change}, exclude=self)

    def set_nickname(self, nickname):
        """
        Set player character's nickname.
        """
        self.db.nick_name = nickname

    def get_name(self):
        """
        Get player character's name.
        """
        # Use nick name instead of normal name.
        return self.db.nick_name

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name, description and available commands.
        info = {"dbref": self.dbref,
                "name": self.get_name(),
                "desc": self.db.desc,
                "cmds": self.get_available_commands(caller)}

        return info

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive():
            commands.append({"name": _("Attack"), "cmd": "attack", "args": self.dbref})
        return commands

    def get_available_channels(self):
        """
        Get available channel's info.

        Returns:
            (dict) channels
        """
        channels = {"": _("Say", category="channels"),
                    "Public": _("Public", category="channels")}

        commands = False
        if self.player:
            if self.is_superuser:
                commands = True
            else:
                for perm in self.player.permissions.all():
                    if perm in settings.PERMISSION_COMMANDS:
                        commands = True
                        break
        if commands:
            channels["cmd"] = _("Cmd")

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

        for room_key in self.db.revealed_map:
            # get room's information
            room = utils.search_obj_data_key(room_key)
            if room:
                room = room[0]
                rooms[room_key] = {"name": room.get_name(),
                                   "icon": room.icon,
                                   "area": room.location and room.location.get_data_key(),
                                   "pos": room.position}

                new_exits = room.get_exits()
                if new_exits:
                    exits.update(new_exits)

        for path in exits.values():
            # add room's neighbours
            if not path["to"] in rooms:
                neighbour = utils.search_obj_data_key(path["to"])
                if neighbour:
                    neighbour = neighbour[0]                    
                    rooms[neighbour.get_data_key()] = {"name": neighbour.get_name(),
                                                       "icon": neighbour.icon,
                                                       "area": neighbour.location and neighbour.location.get_data_key(),
                                                       "pos": neighbour.position}
                    
        return {"rooms": rooms, "exits": exits}

    def show_location(self):
        """
        show character's location
        """
        if self.location:
            location_key = self.location.get_data_key()
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
            reveal_map = None
            if not location_key in self.db.revealed_map:
                # reveal map
                self.db.revealed_map.add(self.location.get_data_key())

                rooms = {location_key: {"name": self.location.get_name(),
                                        "icon": self.location.icon,
                                        "area": self.location.location and self.location.location.get_data_key(),
                                        "pos": self.location.position}}

                exits = self.location.get_exits()

                for path in exits.values():
                    # add room's neighbours
                    if not path["to"] in rooms:
                        neighbour = utils.search_obj_data_key(path["to"])
                        if neighbour:
                            neighbour = neighbour[0]

                            rooms[neighbour.get_data_key()] = {"name": neighbour.get_name(),
                                                               "icon": neighbour.icon,
                                                               "area": neighbour.location and neighbour.location.get_data_key(),
                                                               "pos": neighbour.position}
                    
                msg["reveal_map"] = {"rooms": rooms, "exits": exits}

            # get appearance
            appearance = self.location.get_appearance(self)
            appearance.update(self.location.get_surroundings(self))
            msg["look_around"] = appearance

            self.msg(msg)

    def load_default_objects(self):
        """
        Load character's default objects.
        """
        # get character's model name
        model_name = getattr(self.dfield, "model", None)
        if not model_name:
            model_name = self.get_data_key()
        
        # default objects
        object_records = DATA_SETS.default_objects.objects.filter(character=model_name)

        default_object_ids = set([record.object for record in object_records])

        # add new default objects
        for object_record in object_records:
            if not self.search_inventory(object_record.object):
                obj_list = [{"object": object_record.object, "number": object_record.number}]
                self.receive_objects(obj_list, mute=True)

    def receive_objects(self, obj_list, mute=False, combat=False):
        """
        Add objects to the inventory.

        Args:
            obj_list: (list) a list of object keys and there numbers.
                             list item: {"object": object's key
                                         "number": object's number}
            mute: (boolean) do not send messages to the owner
            combat: (boolean) get objects in combat.

        Returns:
            (dict) a list of objects that not have been received and their reasons.
        """
        accepted_keys = {}      # the keys of objects that have been accepted
        accepted_names = {}     # the names of objects that have been accepted
        rejected_keys = {}      # the keys of objects that have been rejected
        reject_reason = {}      # the reasons of why objects have been rejected

        # check what the character has now
        inventory = {}
        for item in self.contents:
            key = item.get_data_key()
            if key in inventory:
                # if the character has more than one item of the same kind,
                # get the smallest stack.
                if inventory[key].db.number > item.db.number:
                    inventory[key] = item
            else:
                inventory[key] = item

        for obj in obj_list:
            key = obj["object"]
            available = obj["number"]
            number = available
            accepted = 0
            name = ""
            unique = False

            if number == 0:
                # it is an empty object
                if key in inventory:
                    # already has this object
                    accepted_keys[key] = 0
                    accepted_names[name] = 0
                    continue

                object_record = get_object_record(key)
                if not object_record:
                    # can not find object's data record
                    reason = _("Can not get %s.") % name
                    rejected_keys[key] = 0
                    reject_reason[name] = reason
                    continue

                if object_record.can_remove:
                    # remove this empty object
                    accepted_keys[key] = 0
                    accepted_names[name] = 0
                    continue

                # create a new content
                new_obj = build_object(key)
                if not new_obj:
                    reason = _("Can not get %s.") % name
                    rejected_keys[key] = 0
                    reject_reason[name] = reason
                    continue

                name = new_obj.get_name()

                # move the new object to the character
                if not new_obj.move_to(self, quiet=True, emit_to_obj=self):
                    new_obj.delete()
                    reason = _("Can not get %s.") % name
                    rejected_keys[key] = 0
                    reject_reason[name] = reason
                    break

                # accept this object
                accepted_keys[key] = 0
                accepted_names[name] = 0

            else:
                # common number
                # if already has this kind of object
                if key in inventory:
                    # add to current object
                    name = inventory[key].name
                    unique = inventory[key].unique

                    add = number
                    if add > inventory[key].max_stack - inventory[key].db.number:
                        add = inventory[key].max_stack - inventory[key].db.number

                    if add > 0:
                        # increase stack number
                        inventory[key].increase_num(add)
                        number -= add
                        accepted += add

                # if does not have this kind of object, or stack is full
                reason = ""
                while number > 0:
                    if unique:
                        # can not have more than one unique objects
                        reason = _("Can not get more %s.") % name
                        break

                    # create a new content
                    new_obj = build_object(key)
                    if not new_obj:
                        reason = _("Can not get %s.") % name
                        break

                    name = new_obj.get_name()
                    unique = new_obj.unique

                    # move the new object to the character
                    if not new_obj.move_to(self, quiet=True, emit_to_obj=self):
                        new_obj.delete()
                        reason = _("Can not get %s.") % name
                        break

                    # Get the number that actually added.
                    add = number
                    if add > new_obj.max_stack:
                        add = new_obj.max_stack

                    if add <= 0:
                        break

                    new_obj.increase_num(add)
                    number -= add
                    accepted += add

                if accepted > 0:
                    accepted_keys[key] = accepted
                    accepted_names[name] = accepted

                if accepted < available:
                    rejected_keys[key] = available - accepted
                    reject_reason[name] = reason

        if not mute:
            # Send results to the player.
            message = {"get_objects":
                            {"accepted": accepted_names,
                             "rejected": reject_reason,
                             "combat": combat}}
            self.msg(message)
            self.show_inventory()

            # call quest handler
            for key in accepted_keys:
                self.quest_handler.at_objective(defines.OBJECTIVE_OBJECT, key, accepted_keys[key])

        return rejected_keys

    def get_object_number(self, obj_key):
        """
        Get the number of this object.
        Args:
            obj_key: (String) object's key

        Returns:
            int: object number
        """
        objects = self.search_inventory(obj_key)

        # get total number
        sum = 0
        for obj in objects:
            obj_num = obj.get_number()
            sum += obj_num

        return sum

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
        objects = self.search_inventory(obj_key)

        if not objects:
            return True

        obj = objects[0]
        if not obj.unique:
            return True

        if obj.get_number() + number <= obj.max_stack:
            return True

        return False

    def use_object(self, obj, number=1):
        """
        Use an object.

        Args:
            obj: (object) object to use
            number: (int) number to use

        Returns:
            result: (string) the description of the result
        """
        if not obj:
            return _("Can not find this object.")

        if obj.db.number < number:
            return _("Not enough number.")

        # take effect
        try:
            result, used = obj.take_effect(self, number)
            if used > 0:
                # remove used object
                self.remove_object(obj.get_data_key(), used)
            return result
        except Exception, e:
            ostring = "Can not use %s: %s" % (obj.get_data_key(), e)
            logger.log_tracemsg(ostring)

        return _("No effect.")

    def remove_objects(self, obj_list):
        """
        Remove objects from the inventory.

        Args:
            obj_list: (list) a list of object keys and there numbers.
                             list item: {"object": object's key
                                         "number": object's number}

        Returns:
            boolean: success
        """
        success = True
        for item in obj_list:
            if not self.remove_object(item["object"], item["number"], True):
                success = False

        self.show_inventory()
        return success

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
        objects = self.search_inventory(obj_key)

        # get total number
        sum = 0
        for obj in objects:
            obj_num = obj.get_number()
            sum += obj_num

        if sum < number:
            return False

        # remove objects
        to_remove = number
        try:
            for obj in objects:
                obj_num = obj.get_number()
                if obj_num > 0:
                    if obj_num >= to_remove:
                        obj.decrease_num(to_remove)
                        to_remove = 0
                    else:
                        obj.decrease_num(obj_num)
                        to_remove -= obj_num

                    if obj.get_number() <= 0:
                        # If this object can be removed from the inventor.
                        if obj.can_remove:
                            # if it is an equipment, take off it first
                            if getattr(obj, "equipped", False):
                                self.take_off_equipment(obj)
                            obj.delete()

                if to_remove <= 0:
                    break
        except Exception, e:
            logger.log_tracemsg("Can not remove object %s: %s" % (obj_key, e))
            return False

        if to_remove > 0:
            logger.log_err("Remove object error: %s" % obj_key)
            return False

        if not mute:
            self.show_inventory()

        return True

    def search_inventory(self, obj_key):
        """
        Search specified object in the inventory.
        """
        result = [item for item in self.contents if item.get_data_key() == obj_key]
        return result

    def show_inventory(self):
        """
        Send inventory data to player.
        """
        inv = self.return_inventory()
        self.msg({"inventory": inv})

    def return_inventory(self):
        """
        Get inventory's data.
        """
        inv = []
        for item in self.contents:
            info = {"dbref": item.dbref,        # item's dbref
                    "name": item.name,          # item's name
                    "number": item.db.number,   # item's number
                    "desc": item.db.desc,       # item's desc
                    "icon": getattr(item, "icon", None)}  # item's icon
            
            if getattr(item, "equipped", False):
                info["equipped"] = item.equipped
            inv.append(info)

        # sort by created time
        inv.sort(key=lambda x:x["dbref"])

        return inv

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
        status = {"level": {"key": "level",
                            "name": _("LEVEL"),
                            "value": self.db.level,
                            "order": 0},
                  "max_exp": {"key": "max_exp",
                              "name": _("MAX EXP"),
                              "value": self.max_exp,
                              "order": 1},
                  "exp": {"key": "exp",
                          "name": _("EXP"),
                          "value": self.db.exp,
                          "order": 2},
                  "max_hp": {"key": "max_hp",
                             "name": _("MAX HP"),
                             "value": self.max_hp,
                             "order": 3},
                  "hp": {"key": "hp",
                         "name": _("HP"),
                         "value": self.db.hp,
                         "order": 4}}

        order = 5
        for value in CHARACTER_ATTRIBUTES_INFO.all_values():
            status[value["key"]] = {"key": value["key"],
                                    "name": value["name"],
                                    "value": getattr(self.cattr, value["key"]),
                                    "order": order}
            order += 1

        return status

    def show_equipments(self):
        """
        Send equipments to player.
        """
        equipments = self.return_equipments()
        self.msg({"equipments": equipments})

    def return_equipments(self):
        """
        Get equipments' data.
        """
        equipments = {}
        for position in self.db.equipments:
            # in order of positions
            info = None
            if self.db.equipments[position]:
                dbref = self.db.equipments[position]
                for obj in self.contents:
                    if obj.dbref == dbref:
                        info = {"dbref": obj.dbref,
                                "name": obj.name,
                                "desc": obj.db.desc}
            equipments[position] = info

        return equipments

    def equip_object(self, obj):
        """
        Equip an object.
        args: obj(object): the equipment object.
        """
        if obj.location != self:
            raise MudderyError(_("Can not find this equipment."))

        type = obj.type
        position = obj.position

        if position not in self.db.equipments:
            raise MudderyError(_("Can not equip it on this position."))

        if not EQUIP_TYPE_HANDLER.can_equip(self.db.career, type):
            raise MudderyError(_("Can not use this equipment."))

        # Take off old equipment
        if self.db.equipments[position]:
            dbref = self.db.equipments[position]

            for content in self.contents:
                if content.dbref == dbref:
                    content.equipped = False

        # Put on new equipment, store object's dbref.
        self.db.equipments[position] = obj.dbref
        
        # Set object's attribute 'equipped' to True
        obj.equipped = True

        # reset character's attributes
        self.refresh_data()

        message = {"status": self.return_status(),
                   "equipments": self.return_equipments(),
                   "inventory": self.return_inventory()}
        self.msg(message)

        return

    def take_off_position(self, position):
        """
        Take off an object from position.
        """
        if not position in self.db.equipments:
            raise MudderyError(_("Can not find this equipment."))

        if not self.db.equipments[position]:
            raise MudderyError(_("Can not find this equipment."))

        # Set object's attribute 'equipped' to False
        dbref = self.db.equipments[position]

        for obj in self.contents:
            if obj.dbref == dbref:
                obj.equipped = False
                find = True

        self.db.equipments[position] = None

        # reset character's attributes
        self.refresh_data()

        message = {"status": self.return_status(),
                   "equipments": self.return_equipments(),
                   "inventory": self.return_inventory()}
        self.msg(message)

    def take_off_equipment(self, equipment):
        """
        Take off an equipment.
        args: equipment(object): the equipment object.
        """
        if equipment.location != self:
            raise MudderyError(_("Can not find this equipment."))

        if equipment.position in self.db.equipments:
            self.db.equipments[equipment.position] = None
        
        # Set object's attribute 'equipped' to False
        equipment.equipped = False

        # reset character's attributes
        self.refresh_data()

        message = {"status": self.return_status(),
                   "equipments": self.return_equipments(),
                   "inventory": self.return_inventory()}
        self.msg(message)

    def unlock_exit(self, exit):
        """
        Unlock an exit. Add exit's key to character's unlock list.
        """
        exit_key = exit.get_data_key()
        if self.is_exit_unlocked(exit_key):
            return True

        if not exit.can_unlock(self):
            self.msg({"msg": _("Can not open this exit.")})
            return False

        self.db.unlocked_exits.add(exit_key)
        return True

    def is_exit_unlocked(self, exit_key):
        """
        Whether the exit is unlocked.
        """
        return exit_key in self.db.unlocked_exits

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
        skills = []

        skill_dict = self.skill_handler.get_all()
        for key in skill_dict:
            skill = skill_dict[key]
            info = {"key": key,
                    "dbref": skill.dbref,
                    "name": skill.get_name(),
                    "desc": skill.db.desc,
                    "cd_remain": skill.get_remain_cd(),
                    "icon": getattr(skill, "icon", None)}

            skills.append(info)

        return skills

    def at_enter_combat_mode(self, combat_handler):
        """
        Called when the character enters a combat.

        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).at_enter_combat_mode(combat_handler)

        self.show_enter_combat(combat_handler)

    def at_combat_win(self, winners, losers):
        """
        Called when the character wins the combat.
        
        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        self.msg({"combat_finish": {"win": True}})
        
        super(MudderyPlayerCharacter, self).at_combat_win( winners, losers)

        # loot
        # get object list
        loots = None
        for loser in losers:
            obj_list = loser.loot_handler.get_obj_list(self)
            if obj_list:
                if not loots:
                    loots = obj_list
                else:
                    loots.extend(obj_list)

        if loots:
            # give objects to winner
            self.receive_objects(loots, combat=True)

        # call quest handler
        for loser in losers:
            self.quest_handler.at_objective(defines.OBJECTIVE_KILL, loser.get_data_key())

    def at_combat_lose(self, winners, losers):
        """
        Called when the character loses the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        self.msg({"combat_finish": {"lose": True}})
        
        super(MudderyPlayerCharacter, self).at_combat_lose(winners, losers)

    def at_combat_escape(self):
        """
        Called when the character escaped from the combat.

        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).at_combat_escape()

        self.msg({"combat_finish": {"escaped": True}})

    def at_leave_combat_mode(self):
        """
        Called when the character leaves a combat.

        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).at_leave_combat_mode()

        if self.has_player:
            # notify combat finished
            self.msg({"left_combat": True})

            # show status
            self.show_status()

    def show_enter_combat(self, combat_handler):
        """
        Show combat information to the player.

        Returns:
            None
        """
        if not combat_handler:
            return
        # notify character
        self.msg({"joined_combat": True})

        # send messages in order
        self.msg({"combat_info": combat_handler.get_appearance(),
                  "combat_commands": self.get_combat_commands()})

    def resume_combat(self):
        """
        Resume unfinished combat.

        Returns:
            None
        """
        combat_handler = getattr(self.ndb, "combat_handler", None)
        if combat_handler:
            # show combat infomation
            self.show_enter_combat(combat_handler)

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
            self.msg({"msg": _("You will be reborn at {c%(p)s{n in {c%(s)s{n seconds.") %
                             {'p': self.home.get_name(), 's': self.reborn_time}})

    def reborn(self):
        """
        Reborn after being killed.
        """
        super(MudderyPlayerCharacter, self).reborn()

        self.show_status()
        self.msg({"msg": _("You are reborn at {c%s{n.") % self.home.get_name()})

    def save_current_dialogue(self, sentences_list, npc):
        """
        Save player's current dialogues.

        Args:
            sentences_list: the list of current dialogues
            npc: NPC whom the player is talking to.

        Returns:
            None
        """
        if not GAME_SETTINGS.get("auto_resume_dialogues"):
            # Can not auto resume dialogues.
            return

        if not sentences_list:
            self.clear_current_dialogue()
            return

        # Save dialogue's id and sentence's ordinal.
        sentences_begin = [(s["dialogue"], s["sentence"]) for s in sentences_list[0]]
        sentences_all = [(s["dialogue"], s["sentence"]) for s_list in sentences_list for s in s_list]

        npc_key = None
        if npc:
            npc_key = npc.get_data_key()

        location_key = None
        if self.location:
            location_key = self.location.get_data_key()

        self.db.current_dialogue = {"sentences_begin": sentences_begin,
                                    "sentences_all": sentences_all,
                                    "npc": npc_key,
                                    "location": location_key}

        return

    def clear_current_dialogue(self):
        """
        Clear player's current dialogues.

        Returns:
            None
        """
        self.db.current_dialogue = None
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

        if not self.db.current_dialogue:
            return

        current = self.db.current_dialogue
        
        if not current["sentences_begin"]:
            return

        # Check dialogue's location
        if self.location.get_data_key() != current["location"]:
            # If player's location has changed, return.
            return

        # Check npc.
        npc_talking = None
        if current["npc"]:
            npc_list = utils.search_obj_data_key(current["npc"])
            npc_in_location = [npc for npc in npc_list if npc.location == self.location]
            if not npc_in_location:
                # If the NPC has left it's location, return.
                return
            npc_talking = npc_in_location[0]

        sentences_list = [DIALOGUE_HANDLER.get_sentence(s[0], s[1]) for s in current["sentences_begin"]]
        output = DIALOGUE_HANDLER.create_output_sentences(sentences_list, self, npc_talking)
        self.msg({"dialogues_list": [output]})
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

        # Get NPC's sentences_list.
        sentences_list = DIALOGUE_HANDLER.get_npc_sentences_list(self, npc)
        
        self.save_current_dialogue(sentences_list, npc)
        self.msg({"dialogues_list": sentences_list})

    def show_dialogue(self, npc, dialogue, sentence):
        """
        Show a dialogue.

        Args:
            npc: (optional) NPC's object.
            dialogue: dialogue's key.
            sentence: sentence's ordinal.

        Returns:
            None
        """
        # Get next sentences_list.
        sentences_list = DIALOGUE_HANDLER.get_next_sentences_list(self,
                                                                  npc,
                                                                  dialogue,
                                                                  sentence,
                                                                  True)

        # Send dialogues_list to the player.
        self.save_current_dialogue(sentences_list, npc)
        self.msg({"dialogues_list": sentences_list})

    def continue_dialogue(self, npc, dialogue, sentence):
        """
        Continue current dialogue.

        Args:
            npc: (optional) NPC's object.
            dialogue: current dialogue's key.
            sentence: current sentence's ordinal.

        Returns:
            None
        """
        if GAME_SETTINGS.get("auto_resume_dialogues"):
            # Check current dialogue.
            if not self.db.current_dialogue:
                return

            if (dialogue, sentence) not in self.db.current_dialogue["sentences_all"]:
                # Can not find specified dialogue in current dialogues.
                return

        try:
            # Finish current sentence
            DIALOGUE_HANDLER.finish_sentence(self, npc, dialogue, sentence)
        except Exception, e:
            ostring = "Can not finish sentence %s-%s: %s" % (dialogue, sentence, e)
            logger.log_tracemsg(ostring)

        # Get next sentences_list.
        sentences_list = DIALOGUE_HANDLER.get_next_sentences_list(self,
                                                                  npc,
                                                                  dialogue,
                                                                  sentence,
                                                                  False)

        # Send dialogues_list to the player.
        self.save_current_dialogue(sentences_list, npc)
        self.msg({"dialogues_list": sentences_list})

    def add_exp(self, exp, combat=False):
        """
        Add character's exp.
        Args:
            exp: (number) the exp value to add.
            combat: (boolean) get exp in combat.
        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).add_exp(exp)

        self.msg({"get_exp": {"exp": exp,
                              "combat": combat}})

    def level_up(self):
        """
        Upgrade level.

        Returns:
            None
        """
        super(MudderyPlayerCharacter, self).level_up()

        # notify the player
        self.msg({"msg": _("{c%s upgraded to level %s.{n") % (self.get_name(), self.db.level)})

    def say(self, channel, message):
        """
        Say something in the channel.

        Args:
            channel: (string) channel's key.
            message: (string) message to say.

        Returns:
            None
        """
        if not (channel in self.available_channels):
            self.msg({"alert":_("You can not say here.")})
            return

        # Build the string to emit to neighbors.
        emit_string = "%s: %s" % (self.get_name(), message)
            
        if not channel:
            # Say in the room.
            solo_mode = GAME_SETTINGS.get("solo_mode")
            if solo_mode:
                self.msg(emit_string)
            else:
                self.location.msg_contents(emit_string)
        else:
            channels = ChannelDB.objects.filter(db_key=channel)
            if not channels:
                self.msg(_("You can not talk in this channel."))
                return
                
            channel_obj = channels[0]
            if not channel_obj.access(self, channel, "send"):
                self.msg(_("You can not access this channel."))
                return

            channel_obj.msg(emit_string)
