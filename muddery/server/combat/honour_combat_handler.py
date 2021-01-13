"""
Combat handler.
"""

from muddery.server.combat.base_combat_handler import BaseCombatHandler
from muddery.server.utils.honours_handler import HONOURS_HANDLER


class HonourCombatHandler(BaseCombatHandler):
    """
    This implements the honour combat handler.
    """
    def at_server_shutdown(self):
        """
        This hook is called whenever the server is shutting down fully
        (i.e. not for a restart).
        """
        for char in self.characters.values():
            # Stop auto cast skills
            character = char["char"]
            character.stop_auto_combat_skill()

        super(HonourCombatHandler, self).at_server_shutdown()

    def show_combat(self, character):
        """
        Show combat information to a character.
        Args:
            character: (object) character

        Returns:
            None
        """
        super(HonourCombatHandler, self).show_combat(character)

        # send messages in order
        character.msg({"combat_commands": character.get_combat_commands()})

    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for char in self.characters.values():
            # Stop auto cast skills
            character = char["char"]
            character.stop_auto_combat_skill()

        super(HonourCombatHandler, self).finish()

    def calc_combat_rewards(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        rewards = super(HonourCombatHandler, self).calc_combat_rewards(winners, losers)

        # set honour
        HONOURS_HANDLER.set_honours(winners, losers)
        for char in self.characters.values():
            character = char["char"]
            character.show_rankings()
            character.show_status()

        return rewards

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset
        """
        super(HonourCombatHandler, self)._cleanup_character(character)

        # Recover all hp.
        character.db.hp = character.max_hp
        if character.has_account:
            character.show_status()
