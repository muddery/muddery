"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from collections import deque
import time
import math
from twisted.internet import reactor
from evennia.utils import logger
from evennia.utils.search import search_object
from muddery.dao.honours_mapper import HONOURS_MAPPER


class MatchQueueHandler(object):
    """
    This model translates default strings into localized strings.
    """
    max_candidates = 20
    max_honour_diff = 200
    min_waiting_time = 5
    preparing_time = 10
    ave_samples_number = 20
    
    def __init__(self):
        """
        Initialize handler
        """
        self.queue = deque()
        self.waiting_time = {}
        self.preparing = {}
        self.ave_samples = deque()
        self.ave_waiting = -1

    def add(self, character):
        """
        Add a character to the queue.
        """
        character_id = character.id

        if character_id in self.waiting_time:
            return
        
        self.queue.append(character_id)
        self.waiting_time[character_id] = time.time()
        character.msg({"in_combat_queue": self.ave_waiting})
        
    def remove(self, character):
        """
        Remove a character from the queue.
        """
        character_id = character.id

        if character_id in self.waiting_time:
            del self.waiting_time[character_id]
            self.queue.remove(character_id)
            
            if character_id in self.preparing:
                opponent = self.preparing[character_id]["opponent"]
                del self.preparing[opponent]
                character = search_object("#%s" % opponent)
                if character:
                    character.msg({"prepare_match_canceled": ""})
                del self.preparing[character_id]

            character.msg({"left_combat_queue": ""})

    def match(self):
        """
        Match opponents according to character's scores.
        The longer a character in the queue, the score is higher.
        The nearer of two character's rank, the score is higher.
        """
        if len(self.queue) < 2:
            return

        time_now = time.time()
        candidates = []
        count = 0
        max = self.max_candidates
        for id in self.queue:
            if count >= max:
                break
                
            if id in self.preparing:
                continue
                
            character = search_object("#%s" % id)
            if character.is_in_combat():
                continue

            candidates.append(id)
            count += 1

        max_score = 0
        opponents = ()
        for i in xrange(len(candidates) - 1):
            for j in xrange(i + 1, len(candidates)):
                score_A = time_now - self.waiting_time[candidates[i]]
                score_B = time_now - self.waiting_time[candidates[j]]
                honour_A = HONOURS_MAPPER.get_honour_by_id(candidates[i], 0)
                honour_B = HONOURS_MAPPER.get_honour_by_id(candidates[j], 0)
                score_C = self.max_honour_diff - math.fabs(honour_A - honour_B)

                if score_A <= self.min_waiting_time or score_B <= self.min_waiting_time or score_C <= 0:
                    break

                score = score_A + score_B + score_C
                if score > max_score:
                    max_score = score
                opponents = i, j
        
        if opponents:
            self.preparing[opponents[0]] = {"time": time.time(),
                                            "opponent": opponents[1]}
            self.preparing[opponents[1]] = {"time": time.time(),
                                            "opponent": opponents[0]}
            character_A = search_object("#%s" % opponents[0])
            character_B = search_object("#%s" % opponents[1])
            if character_A:
                character_A.msg({"prepare_match": self.preparing_time})
            if character_B:
                character_B.msg({"prepare_match": self.preparing_time})
            reactor.callLater(self.preparing_time, self.fight, opponents)

            self.ave_samples.append(self.waiting_time[opponents[0]])
            self.ave_samples.append(self.waiting_time[opponents[1]])

            while len(self.ave_samples) > self.ave_samples_number:
                self.ave_samples.popleft()

            self.ave_waiting = float(sum(self.ave_samples)) / len(self.ave_samples)

    def fight(self, opponents):
        """
        Create a combat.
        """
        print("opponents: %s" % opponents)

# main handler
MATCH_QUEUE_HANDLER = MatchQueueHandler()

