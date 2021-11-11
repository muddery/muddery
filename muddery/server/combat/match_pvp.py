"""
This model translates default strings into localized strings.
"""

from collections import deque
import time
import math
from django.conf import settings
from twisted.internet import reactor
from twisted.internet import task
from evennia import create_script
from muddery.server.database.gamedata.honours_mapper import HONOURS_MAPPER
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.defines import CombatType
from muddery.server.database.worlddata.honour_settings import HonourSettings
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.server import Server


class MatchPVPHandler(object):
    """
    This model translates default strings into localized strings.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.max_honour_diff = 0
        self.preparing_time = 0
        self.match_interval = 10

        # waiting_queue: a list of character's db id
        self.waiting_queue = deque()

        # preparing:
        #   character's db id: {
        #       "time": begin time,
        #       "opponent": match's opponent,
        #       "confirmed": confirmed the combat,
        #       "call_id": waiting caller's id,
        #   }
        self.preparing = {}

        self.loop = None

        self.reset()
        
    def __del__(self):
        """
        Clear all resources.
        """
        if self.loop and self.loop.running:
            self.loop.stop()

        self.remove_all()

    def remove_all(self):
        """
        # Remove all characters in the waiting queue.
        """
        for char_db_id, info in self.preparing.values():
            call_id = info["call_id"]
            call_id.cancel()

            try:
                character = Server.world.get_character(char_db_id)
                character.msg({"match_rejected": char_db_id})
            except Exception:
                pass

        self.preparing.clear()

        for char_db_id in self.waiting_queue:
            try:
                character = Server.world.get_character(char_db_id)
                character.msg({"left_combat_queue": ""})
            except Exception:
                pass

        self.waiting_queue.clear()

    def reset(self):
        """
        Reset the waiting queue.
        """
        if self.loop and self.loop.running:
            self.loop.stop()

        # Remove all characters in the waiting queue.
        self.remove_all()

        honour_settings = HonourSettings.get_first_data()
        if honour_settings:
            self.max_honour_diff = honour_settings.max_honour_diff
            self.preparing_time = honour_settings.preparing_time
            self.match_interval = honour_settings.match_interval

        self.loop = task.LoopingCall(self.match)
        self.loop.start(self.match_interval)

    def add(self, character):
        """
        Add a character to the queue.
        """
        char_db_id = character.get_db_id()

        if char_db_id in self.waiting_queue:
            return
        
        self.waiting_queue.append(char_db_id)
        character.msg({"in_combat_queue": ""})

    def remove(self, character):
        """
        Remove a character from the queue.
        """
        char_db_id = character.get_db_id()

        try:
            self.waiting_queue.remove(char_db_id)
        except ValueError:
            pass

        try:
            del self.preparing[char_db_id]
        except KeyError:
            pass

        character.msg({"left_combat_queue": ""})

    def match(self):
        """
        Match opponents according to character's scores.
        The longer a character in the queue, the score is higher.
        The nearer of two character's rank, the score is higher.
        """
        if len(self.waiting_queue) < 2:
            return

        # match characters by honour differences
        for i in range(len(self.waiting_queue) - 1):
            char_id_A = self.waiting_queue[i]
            if char_id_A in self.preparing:
                continue

            for j in range(i + 1, len(self.waiting_queue)):
                char_id_B = self.waiting_queue[j]
                if char_id_B in self.preparing:
                    continue

                honour_A = HONOURS_MAPPER.get_honour(char_id_A, 0)
                honour_B = HONOURS_MAPPER.get_honour(char_id_B, 0)

                # max_honour_diff means no limits
                if self.max_honour_diff == 0 or math.fabs(honour_A - honour_B) <= self.max_honour_diff:
                    # can match
                    try:
                        character = Server.world.get_character(char_id_A)
                        character.msg({"prepare_match": self.preparing_time})
                    except KeyError:
                        pass

                    try:
                        character = Server.world.get_character(char_id_B)
                        character.msg({"prepare_match": self.preparing_time})
                    except KeyError:
                        pass

                    call_id = reactor.callLater(self.preparing_time, self.fight, (char_id_A, char_id_B))
                    self.preparing[char_id_A] = {
                        "time": time.time(),
                        "opponent": char_id_B,
                        "confirmed": False,
                        "call_id": call_id,
                    }
                    self.preparing[char_id_B] = {
                        "time": time.time(),
                        "opponent": char_id_A,
                        "confirmed": False,
                        "call_id": call_id,
                    }

    def confirm(self, character):
        """
        Confirm an honour combat.
        """
        char_db_id = character.get_db_id()

        try:
            self.preparing[char_db_id]["confirmed"] = True
        except KeyError:
            pass

    def reject(self, character):
        """
        Reject an honour combat.
        """
        char_db_id = character.get_db_id()
        try:
            info = self.preparing[char_db_id]
        except KeyError:
            return

        # stop the call
        call_id = info["call_id"]
        call_id.cancel()
        
        # remove characters from the preparing queue
        del self.preparing[char_db_id]
        try:
            character = Server.world.get_character(char_db_id)
            character.msg({"match_rejected": char_db_id})
        except KeyError:
            pass

        opponent_db_id = info["opponent"]
        del self.preparing[opponent_db_id]
        try:
            character = Server.world.get_character(opponent_db_id)
            character.msg({"match_rejected": char_db_id})
        except KeyError:
            pass

        self.remove(character)

    def fight(self, opponents_id):
        """
        Create a combat.
        """
        def remove_by_id(char_db_id):
            """
            Remove a character from the queue.
            """
            try:
                self.waiting_queue.remove(char_db_id)
            except ValueError:
                pass

            try:
                del self.preparing[char_db_id]
            except KeyError:
                pass

        confirmed0 = opponents_id[0] in self.preparing and self.preparing[opponents_id[0]]["confirmed"]
        confirmed1 = opponents_id[1] in self.preparing and self.preparing[opponents_id[1]]["confirmed"]

        if not confirmed0 and not confirmed1:
            # Neither characters is confirmed.
            remove_by_id(opponents_id[0])
            remove_by_id(opponents_id[1])

            try:
                character = Server.world.get_character(opponents_id[0])
                character.msg({
                    "match_rejected": opponents_id[0],
                    "left_combat_queue": "",
                })
            except KeyError:
                pass

            try:
                character = Server.world.get_character(opponents_id[1])
                character.msg({
                    "match_rejected": opponents_id[1],
                    "left_combat_queue": "",
                })
            except KeyError:
                pass

        elif not confirmed0:
            # Opponents 0 not confirmed.

            # Remove opponent 0.
            remove_by_id(opponents_id[0])

            try:
                character = Server.world.get_character(opponents_id[0])
                character.msg({
                    "match_rejected": opponents_id[0],
                    "left_combat_queue": "",
                })
            except KeyError:
                pass

            # Put opponent 1 back to the waiting queue.
            try:
                del self.preparing[opponents_id[1]]
            except KeyError:
                pass

            try:
                character = Server.world.get_character(opponents_id[1])
                character.msg({
                    "match_rejected": opponents_id[0],
                })
            except KeyError:
                pass

        elif not confirmed1:
            # opponents 1 not confirmed

            # Remove opponent 1.
            remove_by_id(opponents_id[1])

            try:
                character = Server.world.get_character(opponents_id[1])
                character.msg({
                    "match_rejected": opponents_id[1],
                    "left_combat_queue": "",
                })
            except KeyError:
                pass

            # Put opponent 0 back to the waiting queue.
            try:
                del self.preparing[opponents_id[0]]
            except KeyError:
                pass

            try:
                character = Server.world.get_character(opponents_id[0])
                character.msg({
                    "match_rejected": opponents_id[1],
                })
            except KeyError:
                pass

        elif confirmed0 and confirmed1:
            # all confirmed

            # create a combat
            opponent0 = Server.world.get_character(opponents_id[0])
            opponent1 = Server.world.get_character(opponents_id[1])

            # create a new combat
            COMBAT_HANDLER.create_combat(
                combat_type=CombatType.HONOUR,
                teams={1:[opponent0], 2:[opponent1]},
                desc=_("Fight of Honour"),
                timeout=0
            )

            remove_by_id(opponents_id[0])
            remove_by_id(opponents_id[1])

            opponent0.msg({"left_combat_queue": ""})
            opponent1.msg({"left_combat_queue": ""})


# main handler
MATCH_COMBAT_HANDLER = MatchPVPHandler()
