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
    combat_timeout = 60
    
    def set_honours(self, winners, losers):
        """
        Set combat winner's honour.
        """
        total_losers = 0
        for char in losers:
            total_losers += HONOURS_MAPPER.get_honour(char)
        average_losers = total_losers / len(losers)
        
        total_winners = 0
        for char in winners:
            total_winners += HONOURS_MAPPER.get_honour(char)
        average_winners = total_winners / len(winners)
        
        total_honours = {}
        for char in winners:
            self_honour = HONOURS_MAPPER.get_honour(char)
            diff = average_losers - self_honour
            change = 0
            if diff > 200:
                change = 20
            elif diff > 100:
                change = 15
            elif diff >= -100:
                change = 10
            elif diff >= -200:
                change = 5
            else:
                change = 0

            value = self_honour + change
            if value < 0:
                value = 0
            total_honours[char.id] = value

        for char in losers:
            self_honour = HONOURS_MAPPER.get_honour(char)
            diff = average_winners - self_honour
            change = 0
            if diff > 200:
                change = 20
            elif diff > 100:
                change = 15
            elif diff >= -100:
                change = 10
            elif diff >= -200:
                change = 5
            else:
                change = 0
        
            value = self_honour - change
            if value < 0:
                value = 0
            total_honours[char.id] = value

        HONOURS_MAPPER.set_honours(total_honours)

                
# main honours handler
HONOURS_HANDLER = HonoursHandler()
