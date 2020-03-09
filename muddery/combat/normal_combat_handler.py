"""
Combat handler.
"""

from django.conf import settings
from muddery.utils import defines
from muddery.utils.builder import delete_object
from muddery.combat.base_combat_handler import BaseCombatHandler


class NormalCombatHandler(BaseCombatHandler):
    """
    This implements the normal combat handler.
    """
    def at_server_shutdown(self):
        """
        This hook is called whenever the server is shutting down fully
        (i.e. not for a restart).
        """
        for character in self.characters.values():
            # Stop auto cast skills
            character.stop_auto_combat_skill()

        super(NormalCombatHandler, self).at_server_shutdown()

    def start_combat(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        super(NormalCombatHandler, self).start_combat()

        for character in self.characters.values():
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
        super(NormalCombatHandler, self).show_combat(character)

        # send messages in order
        character.msg({"combat_commands": character.get_combat_commands()})

    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        for character in self.characters.values():
            # Stop auto cast skills
            character.stop_auto_combat_skill()

        super(NormalCombatHandler, self).finish()

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean
        it of the back-reference and cmdset
        """
        super(NormalCombatHandler, self)._cleanup_character(character)

        if not character.is_typeclass(settings.BASE_PLAYER_CHARACTER_TYPECLASS):
            if character.is_temp:
                # notify its location
                location = character.location
                delete_object(character.dbref)
                if location:
                    for content in location.contents:
                        if content.has_account:
                            content.show_location()
            else:
                if character.is_alive():
                    # Recover.
                    character.recover()
