"""
Combat handler.
"""

from muddery.server.combat.combat_runner.base_combat import BaseCombat
from muddery.server.utils.honours_handler import HONOURS_HANDLER


class HonourCombat(BaseCombat):
    """
    This implements the honour combat handler.
    """
    def __del__(self):
        """
        This hook is called whenever the server is shutting down fully
        (i.e. not for a restart).
        """
        for char in self.characters.values():
            # Stop auto cast skills
            character = char["char"]
            character.stop_auto_combat_skill()

        super(HonourCombat, self).at_server_shutdown()

    def show_combat(self, character):
        """
        Show combat information to a character.
        Args:
            character: (object) character

        Returns:
            None
        """
        super(HonourCombat, self).show_combat(character)

        # send messages in order
        character.msg({"combat_commands": character.get_combat_commands()})

    def calc_combat_rewards(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        # add escaped characters to losers list
        all_losers = {char_id: char["char"] for char_id, char in self.characters.items() if char_id not in winners}
        rewards = super(HonourCombat, self).calc_combat_rewards(winners, all_losers)

        # set honour
        honour_changes = HONOURS_HANDLER.set_honours(winners, all_losers)
        for char_id in self.characters:
            if char_id not in rewards:
                rewards[char_id] = {}
            rewards[char_id]["honour"] = honour_changes[char_id] if char_id in honour_changes else 0

        for char in self.characters.values():
            character = char["char"]
            character.show_rankings()
            character.show_status()

        return rewards
