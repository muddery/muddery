"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.typeclasses.objects import MudderyObject
from muddery.utils.creater import create_object

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
                obj_key = arg[0]
                number = 1
            elif len(arg) >= 2:
                obj_key = arg[0]
                number = int(arg[1])

            self.obj_list[obj_key] = number


    def at_init(self):
        """
        Load world data.
        """
        super(MudderyObjectCreater, self).at_init()

        # need save before modify m2m fields
        self.save()

        self.obj_list = {}

        try:
            self.load_data()
        except Exception, e:
            print "%s can not load data:%s" % (self.dbref, e)


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
        create_object(caller, self.obj_list)
