"""
MudderyNPC is NPC's base class.

"""

import json
from django.conf import settings
from evennia.objects.objects import DefaultObject
from muddery.typeclasses.objects import MudderyObject


class MudderyNPC(MudderyObject):
    """
    Default NPC.
    """
    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        commands = []
        return commands
