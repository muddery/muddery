"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.typeclasses.objects import MudderyObject
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import _


class MudderyCommonObject(MudderyObject):
    """
    This is a common object. Players can put it in their inventories.
    
    There can be a lot of common objects of the same kind in the game, so their haven't
    home and fixed locations.
    
    It has two additional properties: max_stack(int) and unique(bool). They decied the number
    of the object that a player can put in his inventory.
    """
    def at_object_creation(self):
        """
        Set default values.
        """
        super(MudderyCommonObject, self).at_object_creation()

        # set default number
        if not self.attributes.has("number"):
            self.db.number = 0

    def after_data_loaded(self):
        """
        Initial this object.
        """
        super(MudderyCommonObject, self).after_data_loaded()

        # set object stack info
        self.max_stack = getattr(self.dfield, "max_stack", 1)
        self.unique = getattr(self.dfield, "unique", False)
        self.can_remove = getattr(self.dfield, "can_remove", True)
        self.can_discard = getattr(self.dfield, "can_discard", True)

    def get_number(self):
        """
        Get object's number.
        """
        return self.db.number

    def increase_num(self, number):
        """
        Increase object's number.
        """
        if number == 0:
            return
        
        if number < 0:
            raise MudderyError("%s can not increase a negative nubmer." % self.get_data_key())

        if self.max_stack == 1 and self.db.number == 1:
            raise MudderyError("%s can not stack." % self.get_data_key())

        if self.db.number + number > self.max_stack:
            raise MudderyError("%s over stack." % self.get_data_key())
        
        self.db.number += number
        return

    def decrease_num(self, number):
        """
        Decrease object's number.
        """
        if number == 0:
            return

        if number < 0:
            raise MudderyError("%s can not decrease a negative nubmer." % self.get_data_key())

        if self.db.number < number:
            raise MudderyError("%s's number will below zero." % self.get_data_key())
        
        self.db.number -= number
        return

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        if self.db.number > 0:
            if self.location and self.can_discard:
                commands.append({"name":_("Discard"), "cmd":"discard", "args":self.dbref})
        return commands

    def take_effect(self, user, number):
        """
        Use this object.

        Args:
            user: (object) the object who uses this
            number: (int) the number of the object to use

        Returns:
            (result, number):
                result: (string) a description of the result
                number: (int) actually used number
        """
        return _("No effect."), 0


class MudderyFood(MudderyCommonObject):
    """
    This is a food. Players can use it to change their properties, such as hp, mp,
    strength, etc.
    """
    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        if self.db.number > 0:
            commands.append({"name": _("Use"), "cmd": "use", "args": self.dbref})
            if self.location and self.can_discard:
                commands.append({"name": _("Discard"), "cmd": "discard", "args": self.dbref})
        return commands


class MudderyEquipment(MudderyCommonObject):
    """
    This is a equipment. Players can equip it to change their properties, such as attack, defence,
    etc.
    """
    def after_data_loaded(self):
        """
        Load equipments data.
        """
        super(MudderyEquipment, self).after_data_loaded()

        self.type = getattr(self.dfield, "type", "")
        self.position = getattr(self.dfield, "position", "")

    def get_effect_fields(self):
        """
        Get data field names which can add to the user.

        Returns:
            (list) a list of field names.
        """
        return []

    def equip_to(self, user):
        """
        Equip this equipment to the user. It is called when a character equip
        this equipment.

        This implementation uses the simplest way to add equipment effects to
        the user. It simply add equipment's effect fields to the user. The user
        must has attributes that has the same name as the equipment's effects.
        You can implementation this method in another way.

        Args:
            user: (object) the user of the equipment.

        Returns:
            None
        """
        if not user:
            return

        for field_name in self.get_effect_fields():
            value = getattr(user, field_name, 0)
            value += getattr(self.dfield, field_name, 0)
            setattr(user, field_name, value)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        if self.db.number > 0:
            if getattr(self, "equipped", False):
                commands.append({"name":_("Take Off"), "cmd":"takeoff", "args":self.dbref})
            else:
                commands.append({"name":_("Equip"), "cmd":"equip", "args":self.dbref})

                # Can not discard when equipped
                if self.location and self.can_discard:
                    commands.append({"name":_("Discard"), "cmd":"discard", "args":self.dbref})

        return commands


class MudderySkillBook(MudderyCommonObject):
    """
    This is a skill book. Players can use it to learn a new skill.
    """
    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        if self.db.number > 0:
            commands.append({"name": _("Use"), "cmd": "use", "args": self.dbref})
            if self.location and self.can_discard:
                commands.append({"name": _("Discard"), "cmd": "discard", "args": self.dbref})
        return commands

    def take_effect(self, user, number):
        """
        Use this object.

        Args:
            user: (object) the object who uses this
            number: (int) the number of the object to use

        Returns:
            (result, number):
                result: (string) a description of the result
                number: (int) actually used number
        """
        if not user:
            raise ValueError("User should not be None.")

        skill_key = getattr(self.dfield, "skill", None)
        if not skill_key:
            return _("No effect."), 0

        if user.learn_skill(skill_key):
            return _("You learned skill."), 1
        else:
            return _("No effect."), 0
