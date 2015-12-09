"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

import traceback
from django.conf import settings
from django.db.models.loading import get_model
from muddery.typeclasses.characters import MudderyCharacter
from muddery.typeclasses.common_objects import MudderyEquipment
from muddery.utils import utils
from muddery.utils.builder import build_object
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from muddery.utils.quest_handler import QuestHandler
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS
from evennia.utils.utils import lazy_property
from evennia.utils import logger
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
    def quest(self):
        return QuestHandler(self)


    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyPlayerCharacter, self).at_object_creation()

        # Set default data.
        self.db.nickname = ""
        self.db.unlocked_exits = set()
        self.db.revealed_map = set()


    def move_to(self, destination, quiet=False,
                emit_to_obj=None, use_destination=True, to_none=False, move_hooks=True):
        """
        Moves this object to a new location.
        """
        if settings.SOLO_MODE:
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
        self.msg({"msg": LS("Moving to %s ...") % self.location.name})
        self.show_location()


    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        # Send puppet info to the client.
        self.msg({"puppet": self.dbref})

        super(MudderyPlayerCharacter, self).at_post_puppet()

        # send character's data to player
        message = {"status": self.return_status(),
                   "equipments": self.return_equipments(),
                   "inventory": self.return_inventory(),
                   "skills": self.return_skills(),
                   "quests": self.quest.return_quests(),
                   "revealed_map": self.get_revealed_map()}
        self.msg(message)

        # notify its location
        if not settings.SOLO_MODE:
            if self.location:
                change = {"dbref": self.dbref,
                          "name": self.get_name()}
                self.location.msg_contents({"player_online":change}, exclude=self)


    def at_pre_unpuppet(self):
        """
        Called just before beginning to un-connect a puppeting from
        this Player.
        
        """
        if not settings.SOLO_MODE:
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
            commands.append({"name":LS("ATTACK"), "cmd":"attack", "args":self.dbref})
        return commands


    def get_revealed_map(self):
        """
        Get the map that the character has revealed.
        Return value:
            {
                "rooms": {room1's key: (name, position),
                          room2's key: (name, position),
                          ...},
                "paths": {room1's key: {room2's key,
                                        room3's key},
                          room2's key: {room3's key,
                                        room4's key},
                          ...}
            }
        """
        rooms = {}
        neighbours = set()
        paths = {}

        for room_key in self.db.revealed_map:
            # get room's information
            room = utils.search_obj_info_key(room_key)
            if room:
                room = room[0]
                rooms[room_key] = (room.get_name(), room.position)

                for neighbour in room.get_neighbours():
                    # get all neighbours
                    neighbour_key = neighbour.get_info_key()
                    neighbours.add(neighbour_key)

                    if room_key > neighbour_key:
                        if room_key in paths:
                            paths[room_key][neighbour_key] = True
                        else:
                            paths[room_key] = {neighbour_key: True}
                    else:
                        if neighbour_key in paths:
                            paths[neighbour_key][room_key] = True
                        else:
                            paths[neighbour_key] = {room_key: True}

        for neighbour_key in neighbours:
            # add neighbours to rooms
            if not neighbour_key in rooms:
                neighbour = utils.search_obj_info_key(neighbour_key)
                if neighbour:
                    neighbour = neighbour[0]
                    rooms[neighbour_key] = (neighbour.get_name(), neighbour.position)

        return {"rooms": rooms, "paths": paths}


    def show_location(self):
        """
        show character's location
        """
        if self.location:
            location_key = self.location.get_info_key()

            msg = {"current_location": location_key}

            reveal_map = None
            if not location_key in self.db.revealed_map:
                # reveal map
                self.db.revealed_map.add(self.location.get_info_key())

                rooms = {location_key: (self.location.get_name(), self.location.position)}
                paths = {}

                for neighbour in self.location.get_neighbours():
                    # get all neighbours
                    neighbour_key = neighbour.get_info_key()
                    rooms[neighbour_key] = (neighbour.get_name(), neighbour.position)

                    if location_key > neighbour_key:
                        if location_key in paths:
                            paths[location_key][neighbour_key] = True
                        else:
                            paths[location_key] = {neighbour_key: True}
                    else:
                        if neighbour_key in paths:
                            paths[neighbour_key][location_key] = True
                        else:
                            paths[neighbour_key] = {location_key: True}

                msg["reveal_map"] = {"rooms": rooms, "paths": paths}

            # get appearance
            appearance = self.location.get_appearance(self)
            appearance.update(self.location.get_surroundings(self))
            msg["look_around"] = appearance

            self.msg(msg)


    def receive_objects(self, obj_list):
        """
        Add objects to the inventory.
        obj_list: (list) a list of object keys and there numbers.
                         list item: {"object": object's key
                                     "number": object's number}
        """
        accepted_keys = {}      # the keys of objects that have been accepted
        accepted_names = {}     # the names of objects that have been accepted
        rejected_keys = {}      # the keys of objects that have been rejected
        reject_reason = {}      # the reasons of why objects have been rejected

        # check what the character has now
        inventory = {}
        for item in self.contents:
            key = item.get_info_key()
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
                    reason = LS("Can not get more %s.") % name
                    break
                        
                # create a new content
                new_obj = build_object(key)
                if not new_obj:
                    reason = LS("Can not get %s.") % name
                    break

                name = new_obj.name
                unique = new_obj.unique

                # move the new object to the character
                if not new_obj.move_to(self, quiet=True, emit_to_obj=self):
                    new_obj.delete()
                    reason = LS("Can not get %s.") % name
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

            # call quest handler
            self.quest.at_get_object(key, accepted)

        # Send results to the player.
        message = {"get_object":
                        {"accepted": accepted_names,
                         "rejected": reject_reason}}
        self.msg(message)
        self.show_inventory()

        return rejected_keys


    def remove_objects(self, obj_list):
        """
        Remove objects from the inventory.
        obj_list: (list) a list of object keys and there numbers.
                         list item: {"object": object's key
                                     "number": object's number}
        """
        changed = False
        for item in obj_list:
            # decrease object's number
            decrease = item["number"]
            objects = self.search_inventory(item["object"])

            for obj in objects:
                try:
                    obj_num = obj.get_number()
                    if obj_num >= decrease:
                        obj.decrease_num(decrease)
                        decrease = 0
                    else:
                        obj.decrease_num(obj_num)
                        decrease -= obj_num

                    if obj.get_number() <= 0:
                        obj.delete()

                    changed = True
                except Exception, e:
                    ostring = "Can not remove object %s: %s" % (obj.get_info_key(), e)
                    logger.log_tracemsg(ostring)
                    break

                if decrease <= 0:
                    break

        if changed:
            self.show_inventory()


    def use_object(self, obj):
        """
        Use an object.
        """
        if not obj:
            return

        result = ""

        # take effect
        try:
            result = self.take_effect(obj)
        except Exception, e:
            ostring = "Can not use %s: %s" % (obj.get_info_key(), e)
            logger.log_tracemsg(ostring)

        # remove used object
        obj_list = [{"object": obj.get_info_key(),
                     "number": 1}]
        self.remove_objects(obj_list)
                                                                                
        return result


    def search_inventory(self, obj_key):
        """
        Search specified object in the inventory.
        """
        result = [item for item in self.contents if item.get_info_key() == obj_key]
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
                    "desc": item.db.desc}       # item's desc
            if item.is_typeclass("muddery.typeclasses.common_objects.MudderyEquipment", False):
                info["equipped"] = item.equipped
            inv.append(info)
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
        status = {"level": self.db.level,
                  "max_exp": self.max_exp,
                  "exp": self.db.exp,
                  "max_hp": self.max_hp,
                  "hp": self.db.hp,
                  "max_mp": self.max_mp,
                  "mp": self.db.mp,
                  "attack": self.attack,
                  "defence": self.defence}

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
            equipments[LS(position)] = info

        return equipments


    def equip_object(self, obj):
        """
        Equip an object.
        """
        if obj.location != self:
            self.msg({"alert":"You do not have that equipment."})
            return False

        type = obj.type
        position = obj.position
        career = ""

        if not EQUIP_TYPE_HANDLER.can_equip(type, career):
            self.msg({"alert":"Can not equip that equipment."})
            return False

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
        
        return True


    def take_off_position(self, position):
        """
        Take off an object from position.
        """
        if self.db.equipments[position]:
            # Set object's attribute 'equipped' to False
            dbref = self.db.equipments[position]
            
            for obj in self.contents:
                if obj.dbref == dbref:
                    obj.equipped = False

        self.db.equipments[position] = None

        # reset character's attributes
        self.refresh_data()


    def take_off_object(self, obj):
        """
        Take off an object.
        """
        if obj.location != self:
            self.msg({"alert":"You do not have that equipment."})
            return

        self.db.equipments[obj.position] = None
        
        # Set object's attribute 'equipped' to False
        obj.equipped = False

        # reset character's attributes
        self.refresh_data()


    def unlock_exit(self, exit):
        """
        Unlock an exit. Add exit's key to character's unlock list.
        """
        exit_key = exit.get_info_key()
        if self.is_exit_unlocked(exit_key):
            return True

        if not exit.can_unlock(self):
            self.msg({"msg": LS("Can not open this exit.")})
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
        for key in self.db.skills:
            skill = self.db.skills[key]
            info = {"dbref": skill.dbref,
                    "name": skill.get_name(),
                    "desc": skill.db.desc}
            skills.append(info)

        return skills


    def die(self, killers):
        """
        This character is killed. Move it to it's home.
        """
        super(MudderyPlayerCharacter, self).die(killers)
        
        self.msg({"msg": LS("You died.")})

        if settings.PLAYER_REBORN_CD <= 0:
            # Reborn immediately
            self.reborn()
        else:
            # Set reborn timer.
            TICKER_HANDLER.add(self, settings.PLAYER_REBORN_CD, hook_key="reborn")

            self.msg({"msg": LS("You will be reborn at {c%s{n in {c%s{n seconds.") %
                        (self.home.get_name(), settings.PLAYER_REBORN_CD)})


    def reborn(self):
        """
        Reborn after being killed.
        """
        TICKER_HANDLER.remove(self, settings.PLAYER_REBORN_CD)

        # Recover all hp.
        self.db.hp = self.max_hp
        self.show_status()

        # Reborn at its home.
        if self.home:
            self.move_to(self.home, quiet=True)
            self.msg({"msg": LS("You are reborn at {c%s{n.") % self.home.get_name()})
