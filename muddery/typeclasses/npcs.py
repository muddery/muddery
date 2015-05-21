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
        
        data = self.get_data_record()
        if not data:
            return
        
        self.set_dialogue(data.dialogue)


    def set_dialogue(self, data):
        """
        Set NPC's dialogues.
        """
        # set dialogue data
        
        # dialogue_queue stores dialogues' priority in order.
        # Dialogues of higher position have higher priorities. It is useful in
        # conditional dialogues.
        #
        # For example:
        # If the player's hp is lower then 50%, the NPC should use dialogue A,
        # otherwise the NPC should use dialogue B, dialogue A and its conditions
        # need to be put before dialogue B.
        self.dialogues = data


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        commands = [{"name":"TALK", "cmd":"talk", "args":self.dbref}]
        return commands
