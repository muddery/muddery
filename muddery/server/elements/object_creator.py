"""
CommonObject is the object that players can put into their inventory.

"""

from evennia.utils.utils import lazy_property
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.dao.loot_list import CreatorLootList


class MudderyObjectCreator(ELEMENT("WORLD_OBJECT")):
    """
    This object loads attributes from world data on init automatically.
    """
    element_key = "WORLD_OBJECT_CREATOR"
    element_name = _("Object Creator", "elements")
    model_name = "object_creators"

    # initialize loot handler in a lazy fashion
    @lazy_property
    def loot_handler(self):
        return LootHandler(self, CreatorLootList.get(self.get_data_key()))

    def after_data_loaded(self):
        """
        Set data_info to the object."
        """
        super(MudderyObjectCreator, self).after_data_loaded()

        # Load creator info.
        self.loot_verb = self.data.loot_verb if self.data.loot_verb else _("Loot")
        self.loot_condition = self.data.loot_condition

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
