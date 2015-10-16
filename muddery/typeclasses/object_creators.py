"""
CommonObject is the object that players can put into their inventory.

"""

import random
from django.conf import settings
from django.db.models.loading import get_model
from muddery.typeclasses.objects import MudderyObject
from muddery.utils import script_handler


class MudderyObjectCreator(MudderyObject):
    """
    This object loads attributes from world data on init automatically.
    """
    
    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyObjectCreator, self).load_data()

        # Load loot list.
        loot_list = []
        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.OBJECT_LOOT_LIST)
            loot_records = model_obj.objects.filter(provider=self.get_info_key())

            for loot_record in loot_records:
                loot_object = {"object": loot_record.object,
                               "number": loot_record.number,
                               "odds": loot_record.odds,
                               "condition": loot_record.condition}
                loot_list.append(loot_object)
        except Exception, e:
            print "Can't load loot info %s: %s" % (self.get_info_key(), e)

        self.loot_list = loot_list


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        verb = self.verb
        if not verb:
            verb = LS("LOOT");

        commands = [{"name":verb, "cmd":"loot", "args":self.dbref}]
        return commands


    def loot(self, caller):
        """
        Loot objects.
        """
        rand = random.random()

        # Get objects that matches odds and conditions .
        obj_list = [obj for obj in self.loot_list if obj["odds"] > rand and\
                                                     script_handler.match_condition(caller, obj["condition"])]

        if caller:
            # Send to the caller.
            caller.receive_objects(obj_list)
