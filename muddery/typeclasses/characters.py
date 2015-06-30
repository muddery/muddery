"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.typeclasses.objects import MudderyObject
from evennia.objects.objects import DefaultCharacter
from muddery.utils.builder import build_object
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from django.conf import settings

class MudderyCharacter(MudderyObject, DefaultCharacter):
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
    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
            
        """
        super(MudderyCharacter, self).at_object_creation()

        equipments = {}
        for position in settings.EQUIP_POSITIONS:
            equipments[position] = None
        self.db.equipments = equipments


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

        if self.location:
            appearance = self.location.get_appearance(self)
            appearance.update(self.location.get_surroundings(self))
            self.msg({"look_around":appearance})


    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        super(MudderyCharacter, self).at_post_puppet()

        # send status to player
        self.show_status()
        
        # send inventory data to player
        self.show_inventory()
    
    
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
            inv.append({"dbref": item.dbref,
                        "name": item.name,
                        "number": item.db.number,
                        "desc": item.db.desc})
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
        status = {"hp": self.db.hp}
        
        equipments = {}
        for pos in self.db.equipments:
            if self.db.equipments[pos]:
                equipments[pos] = self.db.equipments[pos]
            else:
                equipments[pos] = ""

        status["equipments"] = equipments

        return status


    def use_object(self, obj):
        """
        Use an object.
        """
        pass


    def equip_object(self, obj):
        """
        Equip an object.
        """
        if not obj.location == self:
            self.msg({"alert":"You do not have that equipment."})
            raise MudderyError("Do not have object: %s" % obj.key)
            return

        type = obj.type
        position = obj.position
        career = ""

        if not EQUIP_TYPE_HANDLER.can_equip(type, career):
            self.msg({"alert":"Can not equip that equipment."})
            raise MudderyError("Can not equip object: %s" % obj.key)
            return

        take_off_position(position)
        self.db.equipments[position] = obj
        self.show_status()


    def take_off_position(self, position):
        """
        Take off an object from position.
        """
        self.db.equipments[position] = None


    def take_off_object(self, obj):
        """
        Take off an object.
        """
        if not obj.location == self:
            self.msg({"alert":"You do not have that equipment."})
            return

        take_off_position(obj.position)
