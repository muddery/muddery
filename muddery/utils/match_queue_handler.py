"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from collections import deque
import time
import math
from twisted.internet import reactor
from twisted.internet import task
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
    match_interval = 10
    
    def __init__(self):
        """
        Initialize handler
        """
        self.queue = deque()
        self.waiting_time = {}
        self.preparing = {}
        self.ave_samples = deque()
        self.ave_waiting = -1
        
        self.loop = task.LoopingCall(self.match)
        self.loop.start(self.match_interval)
        
    def __del__(self):
        """
        Clear all resources.
        """
        if self.loop and self.loop.running:
            self.loop.stop()

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

        if character_id in self.waiting_time:
            del self.waiting_time[character_id]
            self.queue.remove(character_id)
            
            if character_id in self.preparing:
                opponent_id = self.preparing[character_id]["opponent"]
                del self.preparing[opponent_id]
                opponent = search_object("#%s" % opponent_id)
                if opponent:
                    opponent[0].msg({"prepare_match_canceled": ""})
                del self.preparing[character_id]

        character.msg({"left_combat_queue": ""})

    def match(self):
        """
        Match opponents according to character's scores.
        The longer a character in the queue, the score is higher.
        The nearer of two character's rank, the score is higher.
        """
        print("match")
        print("queue: %s" % self.queue)
        print("waiting: %s" % self.waiting_time)
        
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
                
            characters = search_object("#%s" % id)
            if not characters or characters[0].is_in_combat():
                continue

            candidates.append(id)
            count += 1

        print("candidates: %s" % candidates)
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
                opponents = candidates[i], candidates[j]
        
        if opponents:
            print("matched")
            print("opponents: %s" % (opponents,))
            self.preparing[opponents[0]] = {"time": time.time(),
                                            "opponent": opponents[1],
                                            "confirmed": False}
            self.preparing[opponents[1]] = {"time": time.time(),
                                            "opponent": opponents[0],
                                            "confirmed": False}
            character_A = search_object("#%s" % opponents[0])
            character_B = search_object("#%s" % opponents[1])
            if character_A:
                character_A[0].msg({"prepare_match": self.preparing_time})
            if character_B:
                character_B[0].msg({"prepare_match": self.preparing_time})
            reactor.callLater(self.preparing_time, self.fight, opponents)

            print("waiting: %s" % self.waiting_time)
            self.ave_samples.append(self.waiting_time[opponents[0]])
            self.ave_samples.append(self.waiting_time[opponents[1]])

            while len(self.ave_samples) > self.ave_samples_number:
                self.ave_samples.popleft()

            self.ave_waiting = float(sum(self.ave_samples)) / len(self.ave_samples)
            
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
            
        opponent_id = self.preparing[character_id]["opponent"]
        opponent = search_object("#%s" % opponent_id)
        if opponent:
            opponent[0].msg({"combat_rejected": True})

        del self.preparing[opponent_id]
        self.remove_by_id(character_id)

    def fight(self, opponents):
        """
        Create a combat.
        """
        print("fight")
        if opponents[0] in self.preparing and self.preparing[opponents[0]]["confirmed"]:
            if opponents[1] in self.preparing and self.preparing[opponents[1]]["confirmed"]:
                print("opponents: %s" % opponents)

        self.remove_by_id(opponents[0])
        self.remove_by_id(opponents[1])

# main handler
MATCH_QUEUE_HANDLER = MatchQueueHandler()

