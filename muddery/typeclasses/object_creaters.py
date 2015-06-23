"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.typeclasses.objects import MudderyObject


class MudderyObjectCreater(MudderyObject):
    """
    This object loads attributes from world data on init automatically.
    """
    
    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyObjectCreater, self).load_data()
        
        data = self.get_data_record()
        if not data:
            return
        
        # set common object's info
        self.obj_list = {}

        for obj in data.obj_list.split(","):
            obj_key = ""
            number = 0
            arg = obj.split(":", 1)
            if len(arg) == 1:
                obj_key = arg[0].strip()
                number = 1
            elif len(arg) >= 2:
                obj_key = arg[0].strip()
                number = int(arg[1].strip())

            self.obj_list[obj_key] = number


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        commands = [{"name":"LOOT", "cmd":"loot", "args":self.dbref}]
        return commands


    def loot(self, caller):
        """
        Loot objects.
        """
        if caller:
            caller.receive_objects(self.obj_list)
