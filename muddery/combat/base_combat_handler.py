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


class BaseCombatHandler(DefaultScript):
    """
    This implements the combat handler.
    """

    # standard Script hooks
    def at_script_creation(self):
        "Called when script is first created"
        self.desc = "handles combat"
        self.interval = 0  # keep running until the battle ends
        self.persistent = False

        # store all combatants
        self.db.characters = {}

        # if battle is finished
        self.db.finished = False

        self.db.timeout = 0

    def _init_character(self, character):
        """
        This initializes handler back-reference 
        and combat cmdset on a character
        """
        if character:
            # add the combat handler
            character.ndb.combat_handler = self

            # Change the command set.
            character.cmdset.add(settings.CMDSET_COMBAT)

            if character.has_player:
                self.show_combat(character)

    def show_combat(self, character):
        """
        Show combat information to a character.
        Args:
            character: (object) character

        Returns:
            None
        """
        # Show combat information to the player.
        character.msg({"joined_combat": True})

        # send messages in order
        character.msg({"combat_info": self.get_appearance()})

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean 
        it of the back-reference and cmdset
        """
        # remove the combat handler
        del character.ndb.combat_handler

        # remove combat commands
        character.cmdset.delete(settings.CMDSET_COMBAT)

        if character.has_player:
            # notify combat finished
            character.msg({"left_combat": True})

            # show status
            character.show_status()

    def at_stop(self):
        "Called just before the script is stopped/destroyed."
        for character in self.db.characters.values():
            # note: the list() call above disconnects list from database
            self._cleanup_character(character)

    def at_server_shutdown(self):
        """
        This hook is called whenever the server is shutting down fully
        (i.e. not for a restart).
        """
        self.stop()

    def set_combat(self, teams, desc, timeout):
        """
        Add combatant to handler
        
        Args:
            teams: (dict) {<team id>: [<characters>]}
            desc: (string) combat's description
            timeout: (int) Total combat time in seconds. Zero means no limit.
        """
        self.db.desc = desc
        self.db.timeout = timeout

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
        pass

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
            
            self.set_combat_results(winners, losers)

        self.stop()

    def set_combat_results(self, winners, losers):
        """
        Called when the character wins the combat.

        Args:
            winners: (List) all combat winners.
            losers: (List) all combat losers.

        Returns:
            None
        """
        for character in winners:
            if character.has_player:
                character.msg({"combat_finish": {"win": True}})

        for character in losers:
            if character.has_player:
                character.msg({"combat_finish": {"lose": True}})

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
        if self.db.finished:
            return

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
            if caller.has_player:
                caller.msg({"combat_finish": {"escaped": True}})

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
