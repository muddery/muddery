"""
Combat handler.
"""

import random
import traceback
from django.conf import settings
from evennia import DefaultScript
from muddery.utils import builder


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

        # if battle is finished
        self.db.finished = False


    def _init_character(self, character):
        """
        This initializes handler back-reference 
        and combat cmdset on a character
        """
        character.ndb.combat_handler = self
        character.cmdset.add("muddery.commands.default_cmdsets.CombatCmdSet")


    def _cleanup_character(self, character):
        """
        Remove character from handler and clean 
        it of the back-reference and cmdset
        """
        del self.db.characters[character.dbref]
        del character.ndb.combat_handler
        character.cmdset.delete("muddery.commands.default_cmdsets.CombatCmdSet")


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
        if not self.db.finished:
            self.msg_all({"combat_finish": {"stopped": True}})

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
        if character.dbref in self.db.characters:
            self._cleanup_character(character)
        if not self.db.characters:
            # if we have no more characters in battle, kill this handler
            self.stop()


    def msg_all(self, message):
        "Send message to all combatants"
        for character in self.db.characters.values():
            character.msg(message)


    def cast_skill(self, skill, caller, target):
        """
        Called by combat commands to cast a skill to the target.

        args:
            skill - (string) skill's key
            caller - (string) caller's dbref
            target - (string) target's dbref
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

        alive = 0
        for character in self.db.characters.values():
            if character.is_alive():
                alive += 1

        if alive < 2:
            # if we have less than 2 characters alive, kill this handler
            self.finish()


    def finish(self):
        """
        """
        winner = []
        for character in self.db.characters.values():
            if character.is_alive():
                winner.append({"dbref": character.dbref,
                               "name": character.name})
        
        self.msg_all({"combat_finish": {"winner": winner}})
        
        # delete dead npcs
        for character in self.db.characters.values():
            if not character.is_alive():
                character.die()
        
        self.db.finished = True
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
