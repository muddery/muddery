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
from muddery.utils.localized_strings_handler import _
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.worlddata.data_sets import DATA_SETS


class MudderyObjectCreator(MudderyObject):
    """
    This object loads attributes from world data on init automatically.
    """

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, DATA_SETS.creator_loot_list.model)

    def after_data_loaded(self):
        """
        Set data_info to the object."
        """
        super(MudderyObjectCreator, self).after_data_loaded()

        # Load creator info.
        self.loot_verb = getattr(self.dfield, "loot_verb", None)
        if not self.loot_verb:
            self.loot_verb = _("Loot")
        self.loot_condition = getattr(self.dfield, "loot_condition", None)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        if not STATEMENT_HANDLER.match_condition(self.loot_condition, caller, self):
            return []

        commands = [{"name": self.loot_verb, "cmd": "loot", "args": self.dbref}]
        return commands

    def loot(self, caller):
        """
        Loot objects.
        """
        self.loot_handler.loot(caller)
