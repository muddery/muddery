"""
Combat handler.
"""

import random
from evennia import DefaultScript
from muddery.utils.combat_rules import resolve_combat


class CombatHandler(DefaultScript):
    """
    This implements the combat handler.
    """

    # standard Script hooks 

    def at_script_creation(self):
        "Called when script is first created"

        self.desc = "handles combat"
        self.interval = 0  # keep running until the battle ends
        self.persistent = True   

        # store all combatants
        self.db.characters = {}


    def _init_character(self, character):
        """
        This initializes handler back-reference 
        and combat cmdset on a character
        """
        character.ndb.combat_handler = self
        character.cmdset.add("muddery.commands.combat.CombatCmdSet")


    def _cleanup_character(self, character):
        """
        Remove character from handler and clean 
        it of the back-reference and cmdset
        """
        dbref = character.id 
        del self.db.characters[dbref]
        del character.ndb.combat_handler
        character.cmdset.delete("muddery.commands.combat.CombatCmdSet")


    def at_start(self):
        """
        This is called on first start but also when the script is restarted
        after a server reboot. We need to re-assign this combat handler to 
        all characters as well as re-assign the cmdset.
        """
        for character in self.db.characters.values():
            self._init_character(character)


    def at_stop(self):
        "Called just before the script is stopped/destroyed."
        for character in self.db.characters.values():
            # note: the list() call above disconnects list from database
            self._cleanup_character(character)


    def at_repeat(self, *args):
        """
        This is called every self.interval seconds or when force_repeat
        is called (because everyone has entered their commands).       

        We let this method take optional arguments (using *args) so we can separate
        between the timeout (no argument) and the controlled turn-end
        where we send an argument.
        """
        return

        if not args:
            self.msg_all("Turn timer timed out. Continuing.")
        self.end_turn()


    # Combat-handler methods

    def add_character(self, character):
        "Add combatant to handler"
        self.db.characters[character.id] = character
        self._init_character(character)
        
        appearance = self.get_appearance()
        self.msg_all({"show_combat": appearance})


    def remove_character(self, character):
        "Remove combatant from handler"
        if character.id in self.db.characters:
            self._cleanup_character(character)
        if not self.db.characters:
            # if we have no more characters in battle, kill this handler
            self.stop()
        else:
            appearance = caller.ndb.combat_handler.get_appearance()
            self.msg_all({"show_combat": appearance})


    def msg_all(self, message):
        "Send message to all combatants"
        for character in self.db.characters.values():
            character.msg(message)


    def set_action(self, action, character, target):
        """
        Called by combat commands to register an action with the handler.

        This resolves all actions by calling the rules module. 
        It then resets everything and starts the next turn. It
        is called by at_repeat().
        """
        resolve_combat(self, action, character, target)

        if len(self.db.characters) < 2:
            # if we have less than 2 characters in battle, kill this handler
            self.msg_all("Combat has ended")
            self.stop()
        else:
            # reset counters before next turn
            for character in self.db.characters.values():
                self.db.characters[character.id] = character


    def get_appearance(self):
        """
        Get the combat appearance.
        """
        appearance = {"characters":[]}
        
        for character in self.db.characters.values():
            info = {"dbref": character.id,
                    "name": character.name,
                    "hp": character.db.hp}
            appearance["characters"].append(info)

        return appearance
