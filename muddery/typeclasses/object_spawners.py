"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.typeclasses.objects import MudderyObject
from muddery.utils.object_creater import create_object

class ObjectSpawner(MudderyObject):
    """
    This object loads attributes from world data on init automatically.
    """
    
    def load_data(self):
        """
            Set data_info to the object."
            """
        super(CommonObject, self).load_data()
        
        data = self.get_data_record()
        if not data:
            return
        
        # set common object's info
        self.spawn_str = data.spawns
        
        
    def set_spawn_list(self, spawn_str)
        """
        Decode spawn_str to spawn_list.
        """
        spawns = spawn_str.split(",")
        for spawn in spawns:
            obj_key = ""
            number = 0
            arg_list = spawn.split(":", 1)
            if len(arg_list) == 1:
                obj_key = arg_list[0]
                number = 1
            elif len(arg_list) >= 2:
                obj_key = arg_list[0]
                number = int(arg_list[1])

            self.spawn_list[obj_key] = number


    def at_init(self):
        """
        Load world data.
        """
        super(ObjectSpawner, self).at_init()

        # need save before modify m2m fields
        self.save()

        self.spawn_str = ""
        self.spawn_list = {}

        try:
            self.load_data()
        except Exception, e:
            logger.log_errmsg("%s can not load data:%s" % (self.dbref, e))


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
        create_object(caller, self.spawn_list)
