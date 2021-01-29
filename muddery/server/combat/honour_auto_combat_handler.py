"""
Combat handler.
"""

from muddery.server.combat.honour_combat_handler import HonourCombatHandler


class HonourAutoCombatHandler(HonourCombatHandler):
    """
    This implements the honour combat handler.
    """
    def start_combat(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        super(HonourAutoCombatHandler, self).start_combat()

        # All characters auto cast skills.
        for char in self.characters.values():
            character = char["char"]
            character.start_auto_combat_skill()

    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for char in self.characters.values():
            character = char["char"]
            character.stop_auto_combat_skill()

        super(HonourAutoCombatHandler, self).finish()
