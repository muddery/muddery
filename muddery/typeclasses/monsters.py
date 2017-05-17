"""
MudderyMob is mob's base class.

"""

import json
import traceback
from django.conf import settings
from evennia.utils import logger
from evennia import TICKER_HANDLER
from muddery.typeclasses.characters import MudderyCharacter
from muddery.utils.builder import delete_object
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS

class MudderyMonster(MudderyCharacter):
    """
    Default mob. Monsters are hostile to players, they can be attacked.
    """
    def after_data_loaded(self):
        """
        Init the character.
        """
        super(MudderyMonster, self).after_data_loaded()

        # set home
        self.home = self.location
        
        self.reborn_cd = GAME_SETTINGS.get("npc_reborn_cd")

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = []
        if self.is_alive():
            commands.append({"name": _("Attack"), "cmd": "attack", "args": self.dbref})
        return commands

    def at_combat_start(self):
        """
        Called when a character enters a combat.

        Args:
            combat_handler: the combat's handler

        Returns:
            None
        """
        super(MudderyMonster, self).at_combat_start()

        # begin auto cast
        self.skill_handler.start_auto_combat_skill()

    def at_combat_win(self, winners, losers):
        """
        Called when the character wins a combat.

        Returns:
            None
        """
        super(MudderyMonster, self).at_combat_win(winners, losers)

        # stop auto cast
        self.skill_handler.stop_auto_combat_skill()

    def at_combat_lose(self, winners, losers):
        """
        Called when the character loses a combat.

        Returns:
            None
        """
        super(MudderyMonster, self).at_combat_lose(winners, losers)

        # stop auto cast
        self.skill_handler.stop_auto_combat_skill()

    def at_leave_combat_mode(self):
        """
        Called when the character leaves a combat.

        Returns:
            None
        """
        super(MudderyMonster, self).at_leave_combat_mode()

        if self.is_alive():
            # Recover all hp.
            self.db.hp = self.max_hp

    def die(self, killers):
        """
        The monster is killed. Reborn in settings.NPC_REBORN_CD seconds.
        """
        try:
            super(MudderyMonster, self).die(killers)
            
            # delete itself and notify its location
            location = self.location

            if self.reborn_cd <= 0:
                # Can not reborn.
                delete_object(self.dbref)
            else:
                # Remove from its location.
                self.move_to(None, quiet=True, to_none=True)
                # Set reborn timer.
                TICKER_HANDLER.add(self.reborn_cd, self.reborn)

            if location:
                for content in location.contents:
                    if content.has_player:
                        content.show_location()
        except Exception, e:
            logger.log_tracemsg("die error: %s" % e)

    def reborn(self):
        """
        Reborn after being killed.
        """
        TICKER_HANDLER.remove(self.reborn_cd, self.reborn)

        # Recover all hp.
        self.db.hp = self.max_hp

        # Reborn at its home.
        if self.home:
            self.move_to(self.home, quiet=True)

            for content in self.home.contents:
                if content.has_player:
                    content.show_location()
