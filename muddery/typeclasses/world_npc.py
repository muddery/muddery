"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from django.conf import settings
from evennia.utils import search
from muddery.utils import utils
from muddery.mappings.typeclass_set import TYPECLASS
from muddery.utils.localized_strings_handler import _


class MudderyWorldNPC(TYPECLASS("BASE_NPC")):
    """
    The character not controlled by players.
    """
    typeclass_key = "WORLD_NPC"
    typeclass_name = _("World NPC", "typeclasses")
    model_name = "world_npcs"

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyWorldNPC, self).after_data_loaded()

        # if it is dead, reborn at init.
        if not self.is_alive():
            if not self.is_temp and self.reborn_time > 0:
                self.reborn()
