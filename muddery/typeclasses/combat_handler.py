"""
Combat handler.
"""

import random
import traceback
from django.conf import settings
from evennia import DefaultScript
from muddery.utils import builder
from evennia import TICKER_HANDLER


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
        del character.ndb.combat_handler
        character.skill.stop_auto_combat_skill()
        character.cmdset.delete("muddery.commands.default_cmdsets.CombatCmdSet")
        if character.has_player:
            character.show_status()


    def at_start(self):
        """
        This is called on first start but also when the script is restarted
        after a server reboot. We need to re-assign this combat handler to 
        all characters as well as re-assign the cmdset.
        """
        for character in self.db.characters.values():
            self._init_character(character)
        self.start_combat()


    def at_stop(self):
        "Called just before the script is stopped/destroyed."
        if not self.db.finished:
            self.msg_all({"combat_finish": {"stopped": True}})

        for character in self.db.characters.values():
            # note: the list() call above disconnects list from database
            self._cleanup_character(character)


    # Combat-handler methods


#    def add_character(self, character):
#        "Add combatant to handler"
#        self.db.characters[character.dbref] = character
#        self._init_character(character)
#
#        # notify character
#        character.msg({"joined_combat": True})
#        message = {"combat_info": self.get_appearance(),
#                   "combat_commands": character.get_combat_commands()}
#        character.msg(message)
#
#        # notify other characters
#        info = {"type": "joined",
#                "dbref": character.dbref,
#                "name": character.name,
#                "max_hp": character.max_hp,
#                "hp": character.db.hp}
#        self.msg_all_combat_process([info])


    def add_characters(self, characters):
        "Add combatant to handler"
        for character in characters:
            self.db.characters[character.dbref] = character
            self._init_character(character)
        
        for character in characters:
            if character.has_player:
                # notify character
                character.msg({"joined_combat": True})
                message = {"combat_info": self.get_appearance(),
                           "combat_commands": character.get_combat_commands()}
                character.msg(message)

        self.start_combat()


    def remove_character(self, character):
        "Remove combatant from handler"
        if character.dbref in self.db.characters:
            self._cleanup_character(character)
            del self.db.characters[character.dbref]
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
            return False

        if not caller in self.db.characters:
            return False
        caller = self.db.characters[caller]

        if target:
            if not target in self.db.characters:
                return False
            target = self.db.characters[target]

        try:
            result = caller.skill.cast_skill(skill, target)
            if result:
                self.msg_all_combat_process(result)
        except Exception, e:
            print "Can not cast skill %s: %s" % (skill, e)
            return False

        alive = 0
        for character in self.db.characters.values():
            if character.is_alive():
                alive += 1

        if alive < 2:
            # if we have less than 2 characters alive, kill this handler
            self.finish()

        return True


    def start_combat(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        for character in self.db.characters.values():
            if not character.has_player:
                character.skill.start_auto_combat_skill()


    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        winner = []
        for character in self.db.characters.values():
            if character.is_alive():
                winner.append({"dbref": character.dbref,
                               "name": character.name})
        
        self.msg_all({"combat_finish": {"winner": winner}})
        
        # delete dead npcs
        kills = [c for c in self.db.characters.values() if not c.is_alive()]

        for kill in kills:
            self._cleanup_character(kill)
            del self.db.characters[kill.dbref]
            kill.die()

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


    def get_all_characters(self):
        """
        Get all characters in combat.
        """
        if not self.db.characters:
            return []

        return self.db.characters.values()


    def msg_all_combat_process(self, process):
        """
        Send combat process to all player characters.
        """
        for character in self.db.characters.values():
            if character.has_player:
                character.msg({"combat_process": process})


    def msg_all_combat_info(self):
        """
        Send combat info to all player characters.
        """
        appearance = self.get_appearance()
        for character in self.db.characters.values():
            if character.has_player:
                character.msg({"combat_info": appearance})
