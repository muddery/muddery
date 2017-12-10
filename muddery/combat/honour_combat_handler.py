"""
Combat handler.
"""

from __future__ import print_function

from muddery.combat.base_combat_handler import BaseCombatHandler
from muddery.utils.honours_handler import HONOURS_HANDLER


class HonourCombatHandler(BaseCombatHandler):
    """
    This implements the honour combat handler.
    """
    def start_combat(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        super(HonourCombatHandler, self).start_combat()

        for character in self.db.characters.values():
            # All characters auto cast skills.
            character.skill_handler.start_auto_combat_skill()

    def set_combat_results(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        super(HonourCombatHandler, self).set_combat_results(winners, losers)

        for character in self.db.characters.values():
            # Stop auto cast skills
            character.skill_handler.stop_auto_combat_skill()

        # set honour
        HONOURS_HANDLER.set_winner_honour(self, winners, losers)
        HONOURS_HANDLER.set_loser_honour(self, winners, losers)
        for character in self.db.characters.values():
            character.show_rankings()
