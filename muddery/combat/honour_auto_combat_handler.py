"""
Combat handler.
"""

from __future__ import print_function

from muddery.combat.base_combat_handler import BaseCombatHandler
from muddery.utils.honours_handler import HONOURS_HANDLER


class HonourAutoCombatHandler(BaseCombatHandler):
    """
    This implements the honour combat handler.
    """
    def start_combat(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        super(HonourAutoCombatHandler, self).start_combat()

        # All characters auto cast skills.
        for character in self.characters.values():
            character.start_auto_combat_skill()

    def at_server_shutdown(self):
        """
        This hook is called whenever the server is shutting down fully
        (i.e. not for a restart).
        """
        for character in self.characters.values():
            character.stop_auto_combat_skill()

        super(HonourAutoCombatHandler, self).at_server_shutdown()

    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for character in self.characters.values():
            character.stop_auto_combat_skill()

        super(HonourAutoCombatHandler, self).finish()

    def set_combat_results(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        super(HonourAutoCombatHandler, self).set_combat_results(winners, losers)

        # set honour
        HONOURS_HANDLER.set_honours(winners, losers)
        for character in self.characters.values():
            character.show_rankings()
            character.show_status()

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset
        """
        super(HonourAutoCombatHandler, self)._cleanup_character(character)

        # Recover all hp.
        character.db.hp = character.max_hp
        if character.has_account:
            character.show_status()
