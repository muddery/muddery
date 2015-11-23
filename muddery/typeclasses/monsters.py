"""
MudderyMob is mob's base class.

"""

import json
import traceback
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger
from muddery.typeclasses.characters import MudderyCharacter
from muddery.utils.builder import delete_object
from muddery.utils.localized_strings_handler import LS

class MudderyMonster(MudderyCharacter):
    """
    Default mob. Monsters are hostile to players, they can be attacked.
    """

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive():
            commands.append({"name":LS("ATTACK"), "cmd":"attack", "args":self.dbref})
        return commands


    def die(self, killers):
        """
        The monster die.
        """
        try:
            super(MudderyMonster, self).die(killers)
            
            # delete itself and notify its location
            location = self.location
            delete_object(self.dbref)

            if location:
                for content in location.contents:
                    if content.has_player:
                        content.show_location()
        except Exception, e:
            logger.log_errmsg("die error: %s" % e)
