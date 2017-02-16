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
            character.at_enter_combat(self)

    def _cleanup_character(self, character):
        """
        Remove character from handler and clean 
        it of the back-reference and cmdset
        """
        if character:
            character.at_leave_combat()

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
#
#        # notify other characters
#        info = {"type": "joined",
#                "dbref": character.dbref,
#                "name": character.name,
#                "max_hp": character.max_hp,
#                "hp": character.db.hp}
#        self.msg_all_combat_process([info])


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
                self._init_character(character)

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
        if self.db.characters:
            # get winners and losers
            winner_team = None
            for character in self.db.characters.values():
                if character.is_alive():
                    winner_team = character.get_team()
                    break

            winners = [c for c in self.db.characters.values() if c.get_team() == winner_team]
            losers = [c for c in self.db.characters.values() if c.get_team() != winner_team]

            if losers:
                # defeated somebody
                # loot
                for winner in winners:
                    if winner.has_player:
                        # get object list
                        loots = None
                        for loser in losers:
                            obj_list = loser.loot_handler.get_obj_list(winner)
                            if obj_list:
                                if not loots:
                                    loots = obj_list
                                else:
                                    loots.extend(obj_list)

                        if loots:
                            # give objects to winner
                            winner.receive_objects(loots)

                # add exp
                for winner in winners:
                    # get total exp
                    exp = 0
                    for loser in losers:
                        exp += loser.provide_exp(winner)

                    if exp:
                        # give experience to the winner
                        winner.add_exp(exp)

                # send result to players
                msg = []
                for winner in winners:
                    msg.append({"dbref": winner.dbref,
                                "name": winner.get_name()})

                self.msg_all({"combat_finish": {"winner": msg}})

                # call quest handler
                for winner in winners:
                    if winner.has_player:
                        for loser in losers:
                            winner.quest_handler.at_objective(defines.OBJECTIVE_KILL, loser.get_data_key())

                # remove dead character
                for loser in losers:
                    self._cleanup_character(loser)
                    del self.db.characters[loser.dbref]
                    loser.die(winners)
            else:
                # no losers, no result
                self.msg_all({"combat_finish": {"stopped": True}})

        self.db.finished = True
        self.stop()


    def get_appearance(self):
        """
        Get the combat appearance.
        """
        appearance = {"characters": [],
                      "desc": self.db.desc}
        
        for character in self.db.characters.values():
            info = {"dbref": character.dbref,
                    "name": character.get_name(),
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
        if not process:
            return

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

    def set_skill_result(self, result):
        """
        Set skill's result.

        Args:
            result: (dict) skill's result

        Returns:
            None
        """
        self.msg_all_combat_process(result)

        if self.can_finish():
            # if this is only one team left, kill this handler
            self.finish()
