"""
Room

Rooms are simple containers that has no location of their own.

"""

import time
from apscheduler.schedulers.background import BackgroundScheduler
from evennia.utils.utils import lazy_property
from evennia.utils import logger
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.database.worlddata.loot_list import RoomProfitList
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _


class MudderyProfitRoom(ELEMENT("ROOM")):
    """
    Characters in this room can get profits.
    """
    element_type = "PROFIT_ROOM"
    element_name = _("Profit Room", "elements")
    model_name = "profit_rooms"

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(RoomProfitList.get(self.get_element_key()))

    def __init__(self):
        """
        Init the element.
        """
        super(MudderyProfitRoom, self).__init__()

        self.scheduler = BackgroundScheduler()
        self.last_trigger_time = {}

    def at_element_setup(self, first_time):
        """
        Set data_info to the object.
        """
        super(MudderyProfitRoom, self).at_element_setup(first_time)

        # add the auto profit job
        if self.scheduler.get_job(self.get_element_key()) is None:
            self.scheduler.add_job(self.put_profits, "interval", seconds=1, id=self.get_element_key())
            self.scheduler.start()

    def at_character_arrive(self, character):
        """
        Called after an object has been moved into this object.

        Args:
        character (Object): The character moved into this one

        """
        super(MudderyProfitRoom, self).at_character_arrive(character)

        if character.is_player():
            if STATEMENT_HANDLER.match_condition(self.const.condition, character, None):
                self.last_trigger_time[character.get_id()] = time.time()

                if self.const.begin_message:
                    character.msg({"msg": self.const.begin_message})

    def at_character_leave(self, character):
        """
        Called when a character leave this room.

        :param character: The character leaving.
        :return:
        """
        char_id = character.get_id()
        if char_id in self.last_trigger_time:
            del self.last_trigger_time[char_id]

            if self.const.end_message:
                character.msg({"msg": self.const.end_message})

    def put_profits(self):
        """
        Set profits to all characters in this room.

        :return:
        """
        current_time = time.time()
        for char_id, last_time in self.last_trigger_time.items():
            if current_time - last_time >= self.const.interval:
                char = self.all_characters[char_id]
                obj_list = self.loot_handler.get_obj_list(char)
                self.last_trigger_time[char_id] = current_time

                if not obj_list:
                    continue

                get_objects = char.receive_objects(obj_list, mute=True)
                if not get_objects:
                    continue

                msg_templates = {item["object_key"]: item["message"] for item in obj_list}
                message = ""
                for item in get_objects:
                    if message:
                        message += ", "

                    template = msg_templates[item["key"]]
                    if template:
                        try:
                            message += template % item["number"]
                        except Exception as e:
                            message += template
                    else:
                        message += _("Get") + " " + item["name"] + " " + str(item["number"])

                char.msg({"msg": message})
