"""
CommonObject is the object that players can put into their inventory.

"""

from __future__ import print_function

import random
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from evennia.utils.utils import lazy_property
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.loot_handler import LootHandler
from muddery.utils.localized_strings_handler import LS
from muddery.utils.script_handler import SCRIPT_HANDLER


class MudderyObjectCreator(MudderyObject):
    """
    This object loads attributes from world data on init automatically.
    """

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, settings.CREATOR_LOOT_LIST)

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
        self.loot_handler.loot(caller)
