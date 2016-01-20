"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.typeclasses.objects import MudderyObject
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS


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
        # set total number
        self.db.number = 0

    def load_data(self):
        """
        Load object data.

        Returns:
            None
        """
        super(MudderyCommonObject, self).load_data()

        # set object stack info
        self.max_stack = getattr(self.dfield, "max_stack", 1)
        self.unique = getattr(self.dfield, "unique", False)

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
            return

        if self.max_stack == 1 and self.db.number == 1:
            raise MudderyError("%s can not stack." % self.get_data_key())
            return

        if self.db.number + number > self.max_stack:
            raise MudderyError("%s over stack." % self.get_data_key())
            return
        
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
            return

        if self.db.number < number:
            raise MudderyError("%s's number will below zero." % self.get_data_key())
            return
        
        self.db.number -= number
        return

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = []
        if self.location:
            commands.append({"name":LS("DISCARD"), "cmd":"discard", "args":self.dbref})
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
        return (LS("No effect."), 0)

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
        commands = [{"name": LS("Use"), "cmd": "use", "args": self.dbref}]
        if self.location:
            commands.append({"name": LS("Discard"), "cmd": "discard", "args": self.dbref})
        return commands


class MudderyEquipment(MudderyCommonObject):
    """
    This is a equipment. Players can equip it to change their properties, such as attack, defence,
    etc.
    """
    def load_data(self):
        """
        Load equipments data.
        """
        super(MudderyEquipment, self).load_data()

        self.type = getattr(self.dfield, "type", "")
        self.position = getattr(self.dfield, "position", "")

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        if getattr(self, "equipped", False):
            commands = [{"name":LS("Take Off"), "cmd":"takeoff", "args":self.dbref}]
        else:
            commands = [{"name":LS("Equip"), "cmd":"equip", "args":self.dbref}]

            # Can not discard when equipped
            if self.location:
                commands.append({"name":LS("DISCARD"), "cmd":"discard", "args":self.dbref})

        return commands
