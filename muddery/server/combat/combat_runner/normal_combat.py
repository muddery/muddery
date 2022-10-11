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
            if not character.is_player():
                # Monsters auto cast skills
                character.start_auto_combat_skill()

    async def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for char in self.characters.values():
            # Stop auto cast skills
            char["char"].stop_auto_combat_skill()

        await super(NormalCombat, self).finish()
