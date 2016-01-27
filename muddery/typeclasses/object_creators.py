"""
CommonObject is the object that players can put into their inventory.

"""

from __future__ import print_function

import random
from django.conf import settings
from django.db.models.loading import get_model
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.script_handler import SCRIPT_HANDLER
from muddery.utils.localized_strings_handler import LS


class MudderyObjectCreator(MudderyObject):
    """
    This object loads attributes from world data on init automatically.
    """
    
    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyObjectCreator, self).load_data()

        # Load creator info.
        self.loot_verb = getattr(self.dfield, "loot_verb", None)
        if not self.loot_verb:
            self.loot_verb = LS("Loot")
        self.loot_condition = getattr(self.dfield, "loot_condition", None)

        # Load loot list.
        loot_list = []
        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.LOOT_LIST)
            loot_records = model_obj.objects.filter(provider=self.get_data_key())

            for loot_record in loot_records:
                loot_object = {"object": loot_record.serializable_value("object"),
                               "number": loot_record.number,
                               "odds": loot_record.odds,
                               "quest": loot_record.serializable_value("quest"),
                               "condition": loot_record.condition}
                loot_list.append(loot_object)
        except Exception, e:
            logger.log_errmsg("Can't load loot info %s: %s" % (self.get_data_key(), e))

        self.loot_list = loot_list


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        if not SCRIPT_HANDLER.match_condition(caller, self, self.loot_condition):
            return []

        commands = [{"name": self.loot_verb, "cmd": "loot", "args": self.dbref}]
        return commands


    def loot(self, caller):
        """
        Loot objects.
        """

        def can_loot(self, looter, obj):
            """
            help function to decide which objects can be looted.
            """
            rand = random.random()
            if obj["odds"] < rand:
                return False

            if obj["quest"]:
                if not looter.quest.is_not_accomplished(obj["quest"]):
                    return False

            if not SCRIPT_HANDLER.match_condition(looter, self, obj["condition"]):
                return False

            return True

        # Get objects that matches odds and conditions .
        obj_list = [obj for obj in self.loot_list if can_loot(self, caller, obj)]

        if caller:
            # Send to the caller.
            caller.receive_objects(obj_list)
