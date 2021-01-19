"""
This model translates default strings into localized strings.
"""

from collections import deque
import time
import math
from django.conf import settings
from twisted.internet import reactor
from twisted.internet import task
from evennia.utils import logger
from evennia import create_script
from evennia.utils.search import search_object
from muddery.server.dao.honours_mapper import HONOURS_MAPPER
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.defines import CombatType
from muddery.server.dao.honour_settings import HonourSettings


class MatchQueueHandler(object):
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

        self.waiting_queue = deque()
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
        for char_id, info in self.preparing.values():
            call_id = info["call_id"]
            call_id.cancel()
            character = search_object("#%s" % char_id)
            if character:
                character.msg({"match_rejected": char_id})
        self.preparing.clear()

        for char_id in self.waiting_queue:
            character = search_object("#%s" % char_id)
            if character:
                character.msg({"left_combat_queue": ""})
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
        self.max_honour_diff = honour_settings.max_honour_diff
        self.preparing_time = honour_settings.preparing_time
        self.match_interval = honour_settings.match_interval

        self.loop = task.LoopingCall(self.match)
        self.loop.start(self.match_interval)

    def add(self, character):
        """
        Add a character to the queue.
        """
        character_id = character.id

        if character_id in self.waiting_queue:
            return
        
        self.waiting_queue.append(character_id)
        character.msg({"in_combat_queue": ""})

    def remove_by_id(self, character_id):
        """
        Remove a character from the queue.
        """
        character = search_object("#%s" % character_id)
        if character:
            self.remove(character[0])

    def remove(self, character):
        """
        Remove a character from the queue.
        """
        character_id = character.id

        if character_id in self.waiting_queue:
            self.waiting_queue.remove(character_id)

        if character_id in self.preparing:
            del self.preparing[character_id]

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

                honour_A = HONOURS_MAPPER.get_honour_by_id(char_id_A, 0)
                honour_B = HONOURS_MAPPER.get_honour_by_id(char_id_B, 0)

                # max_honour_diff means no limits
                if self.max_honour_diff == 0 or math.fabs(honour_A - honour_B) <= self.max_honour_diff:
                    # can match
                    character_A = search_object("#%s" % char_id_A)
                    character_B = search_object("#%s" % char_id_B)
                    if character_A:
                        character_A[0].msg({"prepare_match": self.preparing_time})
                    if character_B:
                        character_B[0].msg({"prepare_match": self.preparing_time})

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
        character_id = character.id
        if character_id not in self.preparing:
            return
            
        self.preparing[character_id]["confirmed"] = True

    def reject(self, character):
        """
        Reject an honour combat.
        """
        character_id = character.id
        if character_id not in self.preparing:
            return

        # stop the call
        call_id = self.preparing[character_id]["call_id"]
        call_id.cancel()
        
        # remove characters from the preparing queue
        opponent_id = self.preparing[character_id]["opponent"]

        character = search_object("#%s" % character_id)
        if character:
            character[0].msg({"match_rejected": character_id})
            del self.preparing[character_id]

        opponent = search_object("#%s" % opponent_id)
        if opponent:
            opponent[0].msg({"match_rejected": character_id})
            del self.preparing[opponent_id]

        self.remove_by_id(character_id)

    def fight(self, opponents):
        """
        Create a combat.
        """
        confirmed0 = opponents[0] in self.preparing and self.preparing[opponents[0]]["confirmed"]
        confirmed1 = opponents[1] in self.preparing and self.preparing[opponents[1]]["confirmed"]

        if not confirmed0 and not confirmed1:
            self.remove_by_id(opponents[0])
            self.remove_by_id(opponents[1])

            opponent0 = search_object("#%s" % opponents[0])
            opponent0[0].msg({"match_rejected": opponents[0],
                              "left_combat_queue": ""})
            opponent1 = search_object("#%s" % opponents[1])
            opponent1[0].msg({"match_rejected": opponents[1],
                              "left_combat_queue": ""})
        elif not confirmed0:
            # opponents 0 not confirmed
            self.remove_by_id(opponents[0])
            if opponents[1] in self.preparing:
                del self.preparing[opponents[1]]

            opponent0 = search_object("#%s" % opponents[0])
            opponent0[0].msg({"match_rejected": opponents[0],
                              "left_combat_queue": ""})

            opponent1 = search_object("#%s" % opponents[1])
            opponent1[0].msg({"match_rejected": opponents[0]})
        elif not confirmed1:
            # opponents 1 not confirmed
            self.remove_by_id(opponents[1])
            if opponents[0] in self.preparing:
                del self.preparing[opponents[0]]

            opponent1 = search_object("#%s" % opponents[1])
            opponent1[0].msg({"match_rejected": opponents[1],
                              "left_combat_queue": ""})

            opponent0 = search_object("#%s" % opponents[0])
            opponent0[0].msg({"match_rejected": opponents[1]})
        elif confirmed0 and confirmed1:
            # all confirmed
            opponent0 = search_object("#%s" % opponents[0])
            opponent1 = search_object("#%s" % opponents[1])
            # create a new combat handler
            chandler = create_script(settings.HONOUR_COMBAT_HANDLER)
            # set combat team and desc
            chandler.set_combat(
                combat_type=CombatType.HONOUR,
                teams={1:[opponent0[0]], 2:[opponent1[0]]},
                desc=_("Fight of Honour"),
                timeout=0
            )

            self.remove_by_id(opponents[0])
            self.remove_by_id(opponents[1])


# main handler
MATCH_QUEUE_HANDLER = MatchQueueHandler()
