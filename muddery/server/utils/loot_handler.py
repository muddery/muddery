"""
LootHandler handles matters of loots.
"""

import random
from evennia.utils import logger
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.localized_strings_handler import _


class LootHandler(object):
    """
    Handles matters of loots.
    """

    def __init__(self, data):
        """
        Initialize handler
        """
        self.loot_list = []

        # load loot data
        loot_list = []
        try:
            for d in data:
                loot_list.append({
                    "object_key": d.object,
                    "number": d.number,
                    "odds": d.odds,
                    "multiple": d.multiple,
                    "message": d.message,
                    "quest": d.quest,
                    "condition": d.condition
                })
        except Exception as e:
            logger.log_errmsg("Can't load loot info %s" % e)

        self.loot_list = loot_list

    def get_obj_list(self, looter, times=1):
        """
        Get loot objects list.

        :param looter:
        :param times:
        :return:
        """
        # Get objects that matches odds and conditions .
        obj_list = []
        rand = random.random()
        for item in self.loot_list:
            # check quests
            if item["quest"]:
                if looter.quest_handler and not looter.quest_handler.is_not_accomplished(item["quest"]):
                    continue

            # check condition
            if not STATEMENT_HANDLER.match_condition(item["condition"], looter, None):
                continue

            if item["multiple"]:
                if rand < item["odds"]:
                    obj_list.append({
                        "object_key": item["object_key"],
                        "number": item["number"] * times,
                        "msg_template": item["message"],
                    })
                rand = random.random()
            else:
                if rand < item["odds"]:
                    obj_list.append({
                        "object_key": item["object"],
                        "number": item["number"] * times,
                        "msg_template": item["message"],
                    })
                    break
                rand -= item["odds"]

        return obj_list
