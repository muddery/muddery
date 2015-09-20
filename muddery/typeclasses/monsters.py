"""
MudderyMob is mob's base class.

"""

import json
import traceback
from django.conf import settings
from django.db.models.loading import get_model
from muddery.typeclasses.characters import MudderyCharacter
from muddery.utils.builder import delete_object

class MudderyMonster(MudderyCharacter):
    """
    Default mob.
    """

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = [{"name":"ATTACK", "cmd":"attack", "args":self.dbref}]
        return commands


    def die(self):
        """
        """
        # delete itself and notify its location
        location = self.location
        delete_object(self.dbref)
        
        if location:
            for content in location.contents:
                if content.has_player:
                    content.show_location();