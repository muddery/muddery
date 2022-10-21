"""
Combat handler.
"""

from muddery.server.combat.combat_runner.honour_combat import HonourCombat


class HonourAutoCombat(HonourCombat):
    """
    This implements the honour combat handler.
    """
    def start(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        super(HonourAutoCombat, self).start()

        # All characters auto cast skills.
        for char in self.characters.values():
            character = char["char"]
            character.start_auto_combat_skill()

    async def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for char in self.characters.values():
            character = char["char"]
            character.stop_auto_combat_skill()

        await super(HonourAutoCombat, self).finish()
