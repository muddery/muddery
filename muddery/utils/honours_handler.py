"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from muddery.dao.honours_mapper import HONOURS_MAPPER


class HonoursHandler(object):
    """
    This model stores all descriptions on all conditions.
    """
    top_rankings_number = 10
    nearest_rankings_number = 10
    opponents_number = 100
    
    def set_winner_honour(self, caller, winners, losers):
        """
        Set combat winner's honour.
        """
        total = 0
        for char in losers:
            total += HONOURS_MAPPER.get_honour(char)
        average = total / len(losers)
        self_honour = HONOURS_MAPPER.get_honour(caller)
        diff = average - self_honour
        if diff > 200:
            add = 20
        elif diff > 100:
            add = 15
        elif diff >= -100:
            add = 10
        elif diff >= -200:
            add = 5
        else:
            add = 0
        HONOURS_MAPPER.set_honour(caller, self_honour + add)

    def set_loser_honour(self, caller, winners, losers):
        """
        Set combat loser's honour.
        """
        total = 0
        for char in winners:
            total += HONOURS_MAPPER.get_honour(char)
        average = total / len(losers)
        self_honour = HONOURS_MAPPER.get_honour(caller)
        diff = average - self_honour
        if diff > 200:
            sub = 0
        elif diff > 100:
            sub = 5
        elif diff >= -100:
            sub = 10
        elif diff >= -200:
            sub = 15
        else:
            sub = 20
        new_honour = self_honour - sub
        if new_honour < 0:
            new_honour = 0
        HONOURS_MAPPER.set_honour(caller, new_honour)
                
# main honours handler
HONOURS_HANDLER = HonoursHandler()
