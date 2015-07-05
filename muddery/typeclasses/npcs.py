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

    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyNPC, self).load_data()

        # set NPC's default dialogues.
        self.set_dialogue(self.dialogue)


    def set_dialogue(self, data):
        """
        Set NPC's dialogues.
        """
        # Set default dialogues.
        # All dialogues which matches the condition will send to the player.
        self.dialogue = data


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        commands = [{"name":"TALK", "cmd":"talk", "args":self.dbref}]
        return commands
