"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.typeclasses.objects import MudderyObject

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
        Set data_info to the object."
        """
        data = self.get_data_record()
        if not data:
            return

        self.set_typeclass(data.typeclass)
        self.set_name(data.name)
        self.set_alias(data.alias)
        self.set_desc(data.desc)
        self.set_lock(data.lock)
        self.set_attributes(data.attributes)
        
        # set common object's info
        self.max_stack = data.max_stack
        self.unique = data.unique
        self.action = data.action
        self.effect = data.effect


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
            raise MudderyError("%s can not increase a negative nubmer." % key)
            return

        if self.max_stack == 1 and self.db.number == 1:
            raise MudderyError("%s can not stack." % key)
            return

        if self.db.number + number > self.max_stack:
            raise MudderyError("%s over stack." % key)
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
            raise MudderyError("%s can not decrease a negative nubmer." % key)
            return

        if self.db.number < number:
            raise MudderyError("%s's number will below zero." % key)
            return
        
        self.db.number -= number
        return


class MudderyFood(MudderyCommonObject):
    """
    This is a food. Players can use it to change their properties, such as hp, mp,
    strength, etc.
    
    Effect field is in the format of:
    <property name>:<effect>,<property name>:<effect>...
    """

    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyFood, self).load_data()

        # convert self.effect from string to dict
        effect = {}
        for arg in self.effect.split(","):
            arg = arg.split(":", 1)
            if len(arg) == 2:
                effect[arg[0].strip()] = arg[1].strip()

        self.effect = effect


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        commands = [{"name":"USE", "cmd":"use", "args":self.dbref}]
        return commands


class MudderyEquipment(MudderyCommonObject):
    """
    This is a equipment. Players can equip it to change their properties, such as attack, defence,
    etc.
    
    Effect field is in the format of:
    <property name>:<effect>,<property name>:<effect>...
    """

    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyFood, self).load_data()

        # convert self.effect from string to dict
        effect = {}
        for arg in self.effect.split(","):
            arg = arg.split(":", 1)
            if len(arg) == 2:
                effect[arg[0].strip()] = arg[1].strip()

        self.effect = effect


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        commands = [{"name":"EQUIP", "cmd":"equip", "args":self.dbref}]
        return commands