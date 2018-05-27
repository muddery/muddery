"""
MudderyMob is mob's base class.

"""

import json
import traceback
from django.conf import settings
from evennia.utils import logger
from muddery.utils.builder import delete_object
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.data_sets import DATA_SETS
from muddery.mappings.typeclass_set import TYPECLASS


class MudderyMonster(TYPECLASS("NON_PLAYER")):
    """
    Default mob. Monsters are hostile to players, they can be attacked.
    """
    key = "MONSTER"

    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyMonster, self).after_data_loaded()

        # set level
        self.db.level = getattr(self.dfield, "level", 1)
        
        # Character can auto fight.
        self.auto_fight = True
        
        # set home
        self.home = self.location
        
        # load dialogues.
        self.load_dialogues()

    def load_dialogues(self):
        """
        Load dialogues.
        """
        npc_key = self.get_data_key()
        dialogues = DATA_SETS.npc_dialogues.objects.filter(npc=npc_key)

        self.default_dialogues = [dialogue.dialogue for dialogue in dialogues if dialogue.default]
        self.dialogues = [dialogue.dialogue for dialogue in dialogues if not dialogue.default]

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive():
            if self.dialogues or self.default_dialogues:
                # If the character have something to talk, add talk command.
                commands.append({"name":_("Talk"), "cmd":"talk", "args":self.dbref})
            
            commands.append({"name": _("Attack"), "cmd": "attack", "args": self.dbref})
        return commands

