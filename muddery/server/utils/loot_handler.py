"""
LootHandler handles matters of loots.
"""

import random
from evennia.utils import logger
from muddery.server.statements.statement_handler import STATEMENT_HANDLER


class LootHandler(object):
    """
    Handles matters of loots.
    """

    def __init__(self, owner, data):
        """
        Initialize handler
        """
        self.owner = owner
        self.loot_list = []

        if not owner:
            return

        # load loot data
        loot_list = []
        try:
            for loot_record in data:
                loot_object = {"object_key": loot_record.object,
                               "number": loot_record.number,
                               "odds": loot_record.odds,
                               "quest": loot_record.quest,
                               "condition": loot_record.condition}
                loot_list.append(loot_object)
        except Exception as e:
            logger.log_errmsg("Can't load loot info %s: %s" % (self.owner.get_object_key(), e))

        self.loot_list = loot_list

    def get_obj_list(self, looter):
        """
        Get a list of objects that dropped.
        
        Returns:
            (list) a list of object's information
        """

        def can_loot(self, looter, obj):
            """
            help function to decide which objects can be looted.
            """
            rand = random.random()
            if obj["odds"] < rand:
                return False

            if obj["quest"]:
                if looter.quest_handler:
                    if not looter.quest_handler.is_not_accomplished(obj["quest"]):
                        return False

            if not STATEMENT_HANDLER.match_condition(obj["condition"], looter, self.owner):
                return False

            return True

        # Get objects that matches odds and conditions .
        obj_list = [obj for obj in self.loot_list if can_loot(self, looter, obj)]

        return obj_list

    def loot(self, looter):
        """
        Loot objects.
        """
        if not looter:
            return

        # Get objects that matches odds and conditions .
        obj_list = self.get_obj_list(looter)

        # Add objects to the looter.
        looter.receive_objects(obj_list)
