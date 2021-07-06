"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.search import get_object_by_key
from muddery.server.utils import search
from muddery.server.utils.localized_strings_handler import _


class MudderyWorldNPC(ELEMENT("BASE_NPC")):
    """
    The character not controlled by players.
    """
    element_type = "WORLD_NPC"
    element_name = _("World NPC", "elements")
    model_name = "world_npcs"

    def after_element_setup(self, first_time):
        """
        Init the character.
        """
        super(MudderyWorldNPC, self).after_element_setup(first_time)

        if not self.is_temp:
            # if it is dead, reborn at init.
            if not self.is_alive() and self.reborn_time > 0:
                self.reborn()

            home = None
            location_key = self.const.location
            if location_key:
                try:
                    home = get_object_by_key(location_key)
                except ObjectDoesNotExist:
                    pass

            self.set_location(home)

    def is_visible(self, caller):
        """
        If this object is visible to the caller.

        Return:
            boolean: visible
        """
        if not self.const.condition:
            return True

        return STATEMENT_HANDLER.match_condition(self.const.condition, caller, self)
