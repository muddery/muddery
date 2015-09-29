"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from django.conf import settings
from django.db.models.loading import get_model
from muddery.typeclasses.characters import MudderyCharacter
from muddery.typeclasses.common_objects import MudderyEquipment
from muddery.utils.builder import build_object
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from muddery.utils.quest_handler import QuestHandler
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS
from evennia.utils.utils import lazy_property
from evennia.utils import logger


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
        self.db.nickname = ""


    def at_object_receive(self, moved_obj, source_location):
        """
        Called after an object has been moved into this object.
        
        Args:
        moved_obj (Object): The object moved into this one
        source_location (Object): Where `moved_object` came from.
        
        """
        super(MudderyCharacter, self).at_object_receive(moved_obj, source_location)

        # send latest inventory data to player
        inv = self.return_inventory()
        self.msg({"inventory":inv})
    
        
    def at_object_left(self, moved_obj, target_location):
        """
        Called after an object has been removed from this object.
        
        Args:
        moved_obj (Object): The object leaving
        target_location (Object): Where `moved_obj` is going.
        
        """
        super(MudderyCharacter, self).at_object_left(moved_obj, target_location)
        
        # send latest inventory data to player
        inv = self.return_inventory()
        self.msg({"inventory":inv})


    def at_after_move(self, source_location):
        """
        We make sure to look around after a move.

        """
        self.msg({"msg": "Moving to %s ..." % self.location.name})
        self.show_location()


    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        self.msg({"puppet": self.dbref})

        super(MudderyCharacter, self).at_post_puppet()

        # send character's data to player
        message = {"status": self.return_status(),
                   "equipments": self.return_equipments(),
                   "inventory": self.return_inventory(),
                   "skills": self.return_skills(),
                   "quests": self.quest.return_quests()}

        self.msg(message)


    def set_nickname(self, nickname):
        """
        Set player character's nickname.
        """
        self.db.nick_name = nickname


    def get_name(self):
        """
        Get player character's name.
        """
        return self.db.nick_name


    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name and description
        info = {"dbref": self.dbref,
                "name": self.get_name(),
                "desc": self.db.desc,
                "cmds": self.get_available_commands(caller)}
    
        return info

    
    def show_location(self):
        """
        show character's location
        """
        if self.location:
            appearance = self.location.get_appearance(self)
            appearance.update(self.location.get_surroundings(self))
            self.msg({"look_around":appearance})


    def receive_objects(self, obj_list):
        """
        Receive objects.
        obj_list: (dict) a list of object keys and there numbers.
        """
        accepted_keys = {}
        accepted_names = {}
        rejected_keys = {}
        rejected_names = {}

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

        for key in obj_list:
            number = obj_list[key]
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
            while number > 0:
                if unique:
                    # can not have more than one unique objects
                    break
                        
                # create a new content
                new_obj = build_object(key)
                if not new_obj:
                    break

                name = new_obj.name
                unique = new_obj.unique

                # move the new object to the character
                if not new_obj.move_to(self, quiet=True, emit_to_obj=self):
                    new_obj.delete()
                    break

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

            if accepted < obj_list[key]:
                rejected_keys[key] = obj_list[key] - accepted
                rejected_names[name] = obj_list[key] - accepted

        message = {"get_object":
                        {"accepted": accepted_names,
                         "rejected": rejected_names}}
        self.msg(message)
        self.show_inventory()

        return rejected_keys


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
        items = self.contents
        for item in items:
            info = {"dbref": item.dbref,
                    "name": item.name,
                    "number": item.db.number,
                    "desc": item.db.desc}
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
        """
        if not obj.location == self:
            self.msg({"alert":"You do not have that equipment."})
            return

        type = obj.type
        position = obj.position
        career = ""

        if not EQUIP_TYPE_HANDLER.can_equip(type, career):
            self.msg({"alert":"Can not equip that equipment."})
            return

        # take off old equipment
        if self.db.equipments[position]:
            dbref = self.db.equipments[position]
            
            for content in self.contents:
                if content.dbref == dbref:
                    content.equipped = False

        # put on new equipment
        self.db.equipments[position] = obj.dbref
        obj.equipped = True

        # reset character's attributes
        self.refresh_data()


    def take_off_position(self, position):
        """
        Take off an object from position.
        """
        if self.db.equipments[position]:
            dbref = self.db.equipments[position]
            
            for obj in self.contents:
                if obj.dbref == dbref:
                    obj.equipped = False

        self.db.equipments[position] = None

        # reset character's attributes
        self.after_equipment_changed()


    def take_off_object(self, obj):
        """
        Take off an object.
        """
        if not obj.location == self:
            self.msg({"alert":"You do not have that equipment."})
            return

        self.db.equipments[obj.position] = None
        obj.equipped = False

        # reset character's attributes
        self.after_equipment_changed()


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
                    "name": skill.name,
                    "desc": skill.db.desc}
            skills.append(info)

        return skills


    def die(self):
        """
        """
        super(MudderyPlayerCharacter, self).die()
        
        self.msg({"msg": "You die."})
        
        # Reborn at its home.
        self.db.hp = self.max_hp
        self.show_status()

        home = self.search(self.home, global_search=True)
        if home:
            self.move_to(home, quiet=True)
            self.msg({"msg": "You are back to %s." % home.name})
