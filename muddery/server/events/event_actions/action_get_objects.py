"""
Event action.
"""

import random
import math
from muddery.server.events.base_interval_action import BaseIntervalAction
from muddery.server.dao.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class ActionGetObjects(BaseIntervalAction):
    """
    Get objects.
    """
    key = "ACTION_GET_OBJECTS"
    name = _("Get Objects", category="event_actions")
    model_name = "action_get_objects"
    repeatedly = True

    def func(self, event_key, character, obj):
        """
        Add objects to the character.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        self.get_object(event_key, character, 1)

    def offline_func(self, event_key, character, obj, times):
        """
        Event action's function when the character is offline.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
            times: (number) event triggered times when the player is offline.
        """
        self.get_object(event_key, character, times)

    def get_object(self, event_key, character, times):
        """
        The character get objects.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            times: (number) event triggered times.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # get object list
        objects_dict = {}
        if times <= 100:
            # Trigger the event only one time.
            for i in range(times):
                rand = random.random()
                for record in records:
                    if record.multiple:
                        if rand < record.odds:
                            if record.object not in objects_dict:
                                objects_dict[record.object] = {
                                    "message": record.message,
                                    "number": record.number,
                                }
                            else:
                                objects_dict[record.object]["number"] += record.number
                        rand = random.random()
                    else:
                        if rand < record.odds:
                            if record.object not in objects_dict:
                                objects_dict[record.object] = {
                                    "message": record.message,
                                    "number": record.number,
                                }
                            else:
                                objects_dict[record.object]["number"] += record.number
                            break
                        rand -= record.odds
        else:
            # If the number of times is too large, simplify the calculation.
            remain_odds = 1.0
            for record in records:
                if record.multiple:
                    # using normal distribution to simulate binomial distribution
                    mean = record.odds * times
                    standard_deviation = math.sqrt(record.odds * times * (1 - record.odds))
                    rand = random.normalvariate(mean, standard_deviation)
                    number = round(rand * remain_odds) * record.number
                    if number > 0:
                        if record.object not in objects_dict:
                            objects_dict[record.object] = {
                                "message": record.message,
                                "number": number,
                            }
                        else:
                            objects_dict[record.object]["number"] += number
                else:
                    odds = record.odds
                    if odds > remain_odds:
                        odds = remain_odds
                    remain_odds -= odds
                    mean = odds * times
                    standard_deviation = math.sqrt(odds * times * (1 - odds))
                    number = round(random.normalvariate(mean, standard_deviation)) * record.number
                    if number > 0:
                        if record.object not in objects_dict:
                            objects_dict[record.object] = {
                                "message": record.message,
                                "number": number,
                            }
                        else:
                            objects_dict[record.object]["number"] += number

        obj_list = [{"object": obj, "number": info["number"]} for obj, info in objects_dict.items()]
        get_objects = character.receive_objects(obj_list, mute=True)

        message = ""
        for item in get_objects:
            if message:
                message += ", "

            template = objects_dict[item["key"]]["message"]
            if template:
                try:
                    message += template % item["number"]
                except:
                    message += template
            else:
                message += _("Get") + " " + item["name"] + " " + str(item["number"])

        if message:
            character.msg(message)
