"""
Combat handler.
"""

from __future__ import print_function

import random
import traceback
from django.conf import settings
from evennia import DefaultScript
from evennia import TICKER_HANDLER
from evennia.utils import logger
from muddery.utils import builder, defines


class MudderyCombatHandler(DefaultScript):
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
        if character:
            character.at_enter_combat_mode(self)

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean 
        it of the back-reference and cmdset
        """
        if character:
            character.at_leave_combat_mode()

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


    def set_combat(self, teams, desc):
        """
        Add combatant to handler
        
        args:
            teams: {<team id>: [<characters>]}
        """
        self.db.desc = desc

        for team in teams:
            for character in teams[team]:
                character.set_team(team)
                self.db.characters[character.dbref] = character

        for character in self.db.characters.values():
            self._init_character(character)

        self.start_combat()

    def remove_character(self, character):
        "Remove combatant from handler"
        if character.dbref in self.db.characters:
            self._cleanup_character(character)
            del self.db.characters[character.dbref]

            if self.can_finish():
                # if we have no more characters in battle, kill this handler
                self.finish()

    def msg_all(self, message):
        "Send message to all combatants"
        for character in self.db.characters.values():
            character.msg(message)

    def can_finish(self):
        """
        Check if can finish this combat. The combat finishes when a team's members
        are all dead.

        Return True or False
        """
        if not self.db.characters:
            return False

        if not len(self.db.characters):
            return False

        teams = set()
        for character in self.db.characters.values():
            if character.is_alive():
                teams.add(character.get_team())
                if len(teams) > 1:
                    return False

        return True

    def start_combat(self):
        """
        Start a combat, make all NPCs to cast skills automatically.
        """
        if self.can_finish():
            # if this is only one team left, kill this handler
            self.finish()
            return

        for character in self.db.characters.values():
            character.at_combat_start()

    def finish(self):
        """
        Finish a combat. Send results to players, and kill all failed characters.
        """
        self.db.finished = True
        
        if self.db.characters:
            # get winners and losers
            winner_team = None
            for character in self.db.characters.values():
                if character.is_alive():
                    winner_team = character.get_team()
                    break

            winners = [c for c in self.db.characters.values() if c.get_team() == winner_team]
            losers = [c for c in self.db.characters.values() if c.get_team() != winner_team]
            
            for character in winners:
                character.at_combat_win(winners, losers)
                
            for character in losers:
                character.at_combat_lose(winners, losers)

        self.stop()

    def get_appearance(self):
        """
        Get the combat appearance.
        """
        appearance = {"desc": self.db.desc,
        			  "characters": []}
        
        for character in self.db.characters.values():
            info = {"dbref": character.dbref,
                    "name": character.get_name(),
                    "team": character.get_team(),
                    "max_hp": character.max_hp,
                    "hp": character.db.hp,
                    "icon": getattr(character, "icon", None)}

            appearance["characters"].append(info)

        return appearance

    def get_all_characters(self):
        """
        Get all characters in combat.
        """
        if not self.db.characters:
            return []

        return self.db.characters.values()

    def prepare_skill(self, skill_key, caller, target):
        """
        Cast a skill.
        """
        if caller:
            caller.cast_skill(skill_key, target)
        
            if self.can_finish():
                # if there is only one team left, kill this handler
                self.finish()

    def skill_escape(self, caller):
        """
        Character escaped by a skill.

        Args:
            caller: (object) the caller of the escape skill.

        Returns:
            None
        """
        if caller:
            caller.at_combat_escape()

            # Skill function will call finish func later, so should not check finish here.
            if caller.dbref in self.db.characters:
                self._cleanup_character(caller)
                del self.db.characters[caller.dbref]
            
    def send_skill_result(self, result):
        """
        Send skill's result to players

        Args:
            result: (dict) skill's result

        Returns:
            None
        """
        for character in self.db.characters.values():
            if character.has_player:
                character.msg({"skill_result": result})
