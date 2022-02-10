"""
LootHandler handles matters of loots.
"""

import random
import math
from muddery.server.utils.logger import logger
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.common.utils.utils import async_gather


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
                    "level": d.level,
                    "number": d.number,
                    "odds": d.odds,
                    "multiple": d.multiple,
                    "message": d.message,
                    "quest": d.quest,
                    "condition": d.condition
                })
        except Exception as e:
            logger.log_err("Can't load loot info %s" % e)

        self.loot_list = loot_list

    async def get_obj_list(self, looter, times=1):
        """
        Get loot objects list.

        :param looter:
        :param times:
        :return:
        """
        # get available loot list
        loot_list = [item for item in self.loot_list if not item["quest"]]
        quest_list = [item for item in self.loot_list if item["quest"]]
        if quest_list:
            accomplished = await async_gather([
                looter.quest_handler.is_not_accomplished(item["quest"]) for item in quest_list
            ])
            loot_list += [item for index, item in enumerate(quest_list) if accomplished[index]]

        if loot_list:
            match = await async_gather([
                STATEMENT_HANDLER.match_condition(item["condition"], looter, None) for item in loot_list
            ])
            available_list = [item for index, item in enumerate(loot_list) if match[index]]
        else:
            available_list = []

        if not available_list:
            return []

        # get object list
        objects_dict = {}
        if times <= 100:
            # Trigger the event only one time.
            for i in range(times):
                rand = random.random()
                for item in available_list:
                    if item["multiple"]:
                        if rand < item["odds"]:
                            if item["object_key"] not in objects_dict:
                                objects_dict[item["object_key"]] = {
                                    "message": item["message"],
                                    "level": item["level"],
                                    "number": item["number"],
                                }
                            else:
                                objects_dict[item["object_key"]]["number"] += item["number"]
                        rand = random.random()
                    else:
                        if rand < item["odds"]:
                            if item["object_key"] not in objects_dict:
                                if item["object_key"] not in objects_dict:
                                    objects_dict[item["object_key"]] = {
                                        "message": item["message"],
                                        "level": item["level"],
                                        "number": item["number"],
                                    }
                                else:
                                    objects_dict[item["object_key"]]["number"] += item["number"]
                            break
                        rand -= item["odds"]
        else:
            # If the number of times is too large, simplify the calculation.
            remain_odds = 1.0
            for item in available_list:
                if item["multiple"]:
                    # using normal distribution to simulate binomial distribution
                    mean = item["odds"] * times
                    standard_deviation = math.sqrt(item["odds"] * times * (1 - item["odds"]))
                    rand = random.normalvariate(mean, standard_deviation)
                    number = round(rand * remain_odds) * item["number"]
                    if number > 0:
                        if item["object_key"] not in objects_dict:
                            objects_dict[item["object_key"]] = {
                                "message": item["message"],
                                "level": item["level"],
                                "number": number,
                            }
                        else:
                            objects_dict[item["object_key"]]["number"] += number
                else:
                    odds = item["odds"]
                    if odds > remain_odds:
                        odds = remain_odds
                    remain_odds -= odds
                    mean = odds * times
                    standard_deviation = math.sqrt(odds * times * (1 - odds))
                    number = round(random.normalvariate(mean, standard_deviation)) * item["number"]
                    if number > 0:
                        if item["object_key"] not in objects_dict:
                            if item["object_key"] not in objects_dict:
                                objects_dict[item["object_key"]] = {
                                    "message": item["message"],
                                    "level": item["level"],
                                    "number": number,
                                }
                            else:
                                objects_dict[item["object_key"]]["number"] += number

        obj_list = [{
            "object_key": object_key,
            "level": item["level"],
            "message": item["message"],
            "number": item["number"],
        } for object_key, item in objects_dict.items()]

        return obj_list
