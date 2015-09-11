"""
Combat handler.
"""

import random
from evennia import DefaultScript
from muddery.utils.combat_rules import resolve_combat
import traceback


class CombatHandler(DefaultScript):
    """
    This implements the combat handler.
    """

    # standard Script hooks 

    def at_script_creation(self):
        "Called when script is first created"

        print "at_script_creation"
        
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
        print "_init_character: %s" % character

        character.ndb.combat_handler = self
        character.cmdset.add("muddery.commands.default_cmdsets.CombatCmdSet")


    def _cleanup_character(self, character):
        """
        Remove character from handler and clean 
        it of the back-reference and cmdset
        """
        print "_cleanup_character: %s" % character
        
        del self.db.characters[character.dbref]
        del character.ndb.combat_handler
        character.cmdset.delete("muddery.commands.default_cmdsets.CombatCmdSet")

        message = {"left_combat": True}
        character.msg(message)


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
        print "add_character: %s" % character
        
        self.db.characters[character.dbref] = character
        self._init_character(character)
        
        # notify character
        character.msg({"joined_combat": True})
        message = {"combat_info": self.get_appearance(),
                   "combat_commands": character.get_combat_commands()}
        character.msg(message)
        
        # notify other characters
        info = {"type": "joined",
                "dbref": character.dbref,
                "name": character.name,
                "max_hp": character.max_hp,
                "hp": character.db.hp}
        self.msg_all_combat_process([info])


    def remove_character(self, character):
        "Remove combatant from handler"
        print "remove_character: %s" % character
        
        if character.dbref in self.db.characters:
            self._cleanup_character(character)
        if not self.db.characters:
            # if we have no more characters in battle, kill this handler
            self.stop()
        else:
            self.msg_all_combat_info()


    def msg_all(self, message):
        "Send message to all combatants"
        for character in self.db.characters.values():
            character.msg(message)


    def cast_skill(self, skill, caller, target):
        """
        Called by combat commands to register an action with the handler.

        This resolves all actions by calling the rules module. 
        It then resets everything and starts the next turn. It
        is called by at_repeat().
        """
        if not skill:
            return

        if not caller in self.db.characters:
            return
        caller = self.db.characters[caller]

        if target:
            if not target in self.db.characters:
                return
            target = self.db.characters[target]

        try:
            result = caller.cast_skill(skill, target)
            if result:
                self.msg_all_combat_process(result)
        except Exception, e:
            print "Can not cast skill %s: %s" % (skill, e)
            print traceback.format_exc()
            return

        if len(self.db.characters) < 2:
            # if we have less than 2 characters in battle, kill this handler
            self.msg_all("Combat has ended")
            self.stop()


    def get_appearance(self):
        """
        Get the combat appearance.
        """
        appearance = {"characters":[]}
        
        for character in self.db.characters.values():
            info = {"dbref": character.dbref,
                    "name": character.name,
                    "max_hp": character.max_hp,
                    "hp": character.db.hp}
            appearance["characters"].append(info)

        print "get_appearance: %s" % appearance

        return appearance


    def msg_all_combat_process(self, process):
        """
        """
        for character in self.db.characters.values():
            if character.has_player:
                character.msg({"combat_process": process})


    def msg_all_combat_info(self):
        """
        """
        appearance = self.get_appearance()
        for character in self.db.characters.values():
            if character.has_player:
                character.msg({"combat_info": appearance})
