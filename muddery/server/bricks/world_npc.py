"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.server.mappings.brick_set import BRICK
from muddery.server.utils.localized_strings_handler import _


class MudderyWorldNPC(BRICK("BASE_NPC")):
    """
    The character not controlled by players.
    """
    brick_key = "WORLD_NPC"
    brick_name = _("World NPC", "bricks")
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
