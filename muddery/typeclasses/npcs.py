"""
MudderyNPC is NPC's base class.

"""

import json
from django.conf import settings
from django.db.models.loading import get_model
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

        # load NPC's dialogues.
        self.load_dialogues()


    def load_dialogues(self):
        """
        Load NPC's dialogues.
        """
        dialogues = []
        model_npc_dialogues = get_model(settings.WORLD_DATA_APP, settings.NPC_DIALOGUES)
        if model_npc_dialogues:
            # Get records.
            npc_key = self.get_info_key()
            dialogues = model_npc_dialogues.objects.filter(npc=npc_key)

        self.dialogues = [dialogue.dialogue_id for dialogue in dialogues]


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        commands = [{"name":"TALK", "cmd":"talk", "args":self.dbref}]
        return commands
