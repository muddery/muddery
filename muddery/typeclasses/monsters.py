"""
MudderyMob is mob's base class.

"""

import json
from django.conf import settings
from django.db.models.loading import get_model
from muddery.typeclasses.characters import MudderyCharacter


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
    