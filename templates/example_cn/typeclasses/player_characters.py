"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

import random
from django.conf import settings
from django.apps import apps
from muddery.typeclasses.player_characters import MudderyPlayerCharacter
from muddery.typeclasses.common_objects import MudderyEquipment
from muddery.utils import defines, utils
from muddery.utils.builder import build_object, get_object_record
from muddery.utils.equip_type_handler import EQUIP_TYPE_HANDLER
from muddery.utils.quest_handler import QuestHandler
from muddery.utils.statement_attribute_handler import StatementAttributeHandler
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils.honours_handler import HONOURS_HANDLER
from muddery.utils.match_queue_handler import MATCH_QUEUE_HANDLER
from muddery.dao.honours_mapper import HONOURS_MAPPER
from muddery.worlddata.data_sets import DATA_SETS
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO
from muddery.utils.utils import get_class
from evennia.utils.utils import lazy_property
from evennia.utils import logger
from evennia.comms.models import ChannelDB
from evennia import create_script


class PlayerCharacter(MudderyPlayerCharacter):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    def return_status(self):
        """
        Get character's status.
        """
        status = {"level": {"key": "level",
                            "name": _("LEVEL"),
                            "value": self.db.level,
                            "order": 0},
                  "max_exp": {"key": "max_exp",
                              "name": _("MAX EXP"),
                              "value": self.max_exp,
                              "order": 1},
                  "exp": {"key": "exp",
                          "name": _("EXP"),
                          "value": self.db.exp,
                          "order": 2},
                  "max_hp": {"key": "max_hp",
                             "name": _("MAX HP"),
                             "value": self.max_hp,
                             "order": 3},
                  "hp": {"key": "hp",
                         "name": _("HP"),
                         "value": self.db.hp,
                         "order": 4},
                  "mp": {"key": "mp",
                         "name": _("MP"),
                         "value": self.db.mp,
                         "order": 5},
                  "max_mp": {"key": "max_mp",
                         "name": _("MAX_MP"),
                         "value": self.max_mp,
                         "order": 6}}

        order = 7
        for value in CHARACTER_ATTRIBUTES_INFO.all_values():
            status[value["key"]] = {"key": value["key"],
                                    "name": value["name"],
                                    "value": getattr(self.cattr, value["key"]),
                                    "order": order}
            order += 1

        return status
