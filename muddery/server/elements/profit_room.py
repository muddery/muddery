"""
Room

Rooms are simple containers that has no location of their own.

"""

import time
from apscheduler.schedulers.background import BackgroundScheduler
from evennia.utils.utils import lazy_property
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.database.worlddata.loot_list import RoomProfitList
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.utils import is_player
from muddery.server.utils.localized_strings_handler import _


class MudderyProfitRoom(ELEMENT("ROOM")):
    """
    Characters in this room can get profits.
    """
    element_type = "PROFIT_ROOM"
    element_name = _("Profit Room", "elements")
    model_name = "world_profit_rooms"

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
        if self.scheduler.get_job(self.self.get_id()) is not None:
            self.scheduler.add_job(self.put_profits, "interval", seconds=1, id=self.get_id())
            self.scheduler.start()

    def at_character_arrive(self, character):
        """
        Called after an object has been moved into this object.

        Args:
        character (Object): The character moved into this one

        """
        super(MudderyProfitRoom, self).at_character_arrive(character)

        if is_player(character):
            self.last_trigger_time[character.get_id()] = 0

    def at_character_leave(self, character):
        """
        Called when a character leave this room.

        :param character: The character leaving.
        :return:
        """
        if is_player(character):
            del self.last_time[character.get_id()]

    def put_profits(self):
        """
        Set profits to all characters in this room.

        :return:
        """
        current_time = time.time()
        for char_id, last_time in self.last_trigger_time.items():
            if current_time - last_time >= self.const.interval:
                self.loot_handler.loot(self.all_characters[char_id])
