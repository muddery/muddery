"""
Combat handler.
"""

from muddery.server.combat.combat_runner.base_combat import BaseCombat


class NormalCombat(BaseCombat):
    """
    This implements the normal combat handler.
    """
    def start(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        super(NormalCombat, self).start()

        for char in self.characters.values():
            character = char["char"]
            if not character.account:
                # Monsters auto cast skills
                character.start_auto_combat_skill()

    def show_combat(self, character):
        """
        Show combat information to a character.
        Args:
            character: (object) character

        Returns:
            None
        """
        super(NormalCombat, self).show_combat(character)

        # send messages in order
        character.msg({"combat_commands": character.get_combat_commands()})

    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for char in self.characters.values():
            # Stop auto cast skills
            char["char"].stop_auto_combat_skill()

        super(NormalCombat, self).finish()
