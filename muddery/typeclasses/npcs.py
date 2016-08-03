"""
MudderyNPC is NPC's base class.

"""

import json
import traceback
from django.conf import settings
from django.apps import apps
from evennia import TICKER_HANDLER
from muddery.typeclasses.characters import MudderyCharacter
from muddery.utils.localized_strings_handler import LS
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils.game_settings import GAME_SETTINGS


class MudderyNPC(MudderyCharacter):
    """
    Default NPC. NPCs are friendly to players, they can not be attacked.
    """
    def load_data(self):
        """
        Init the character.
        """
        super(MudderyNPC, self).load_data()

        # set home
        self.home = self.location

        # load dialogues.
        self.load_dialogues()
        
        self.reborn_cd = GAME_SETTINGS.get("npc_reborn_cd")


    def load_dialogues(self):
        """
        Load dialogues.
        """
        dialogues = []
        model_npc_dialogues = apps.get_model(settings.WORLD_DATA_APP, settings.NPC_DIALOGUES)
        if model_npc_dialogues:
            # Get records.
            npc_key = self.get_data_key()
            dialogues = model_npc_dialogues.objects.filter(npc=npc_key)

        self.default_dialogues = [dialogue.dialogue for dialogue in dialogues if dialogue.default]
        self.dialogues = [dialogue.dialogue for dialogue in dialogues if not dialogue.default]


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.dialogues or self.default_dialogues:
            # If the character have something to talk, add talk command.
            commands.append({"name":LS("Talk"), "cmd":"talk", "args":self.dbref})
        return commands


    def have_quest(self, caller):
        """
        If the npc can complete or provide quests.
        Returns (can_provide_quest, can_complete_quest).
        """
        return DIALOGUE_HANDLER.have_quest(caller, self)


    def die(self, killers):
        """
        This npc is killed. Reborn in settings.NPC_REBORN_CD seconds.
        """
        super(MudderyNPC, self).die(killers)

        location = self.location

        if self.reborn_cd <= 0:
            # Can not reborn.
            delete_object(self.dbref)
        else:
            # Remove from its location.
            self.move_to(None, quiet=True, to_none=True)
            # Set reborn timer.
            TICKER_HANDLER.add(self, self.reborn_cd, hook_key="reborn")

        if location:
            for content in location.contents:
                if content.has_player:
                    content.show_location()


    def reborn(self):
        """
        Reborn after being killed.
        """
        TICKER_HANDLER.remove(self, self.reborn_cd)

        # Recover all hp.
        self.db.hp = self.max_hp

        # Reborn at its home.
        if self.home:
            self.move_to(self.home, quiet=True)

            for content in self.home.contents:
                if content.has_player:
                    content.show_location()
