"""
This model translates default strings into localized strings.
"""

from muddery.server.database.gamedata.honours_mapper import HONOURS_MAPPER


class HonoursHandler(object):
    """
    This model stores all descriptions on all conditions.
    """
    def set_honours(self, winners, losers):
        """
        Set combat winner's honour.
        """
        total_losers = 0
        average_losers = 0
        if losers:
            for char in losers:
                total_losers += HONOURS_MAPPER.get_honour_by_id(char, 0)
            average_losers = total_losers / len(losers)
        
        total_winners = 0
        average_winners = 0
        if winners:
            for char in winners:
                total_winners += HONOURS_MAPPER.get_honour_by_id(char, 0)
            average_winners = total_winners / len(winners)

        honour_changes = {}
        total_honours = {}
        for char in winners:
            # Calculate the change of the honour.
            self_honour = HONOURS_MAPPER.get_honour_by_id(char, 0)
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
            honour_changes[char] = value - self_honour
            total_honours[char] = value

        for char in losers:
            # Calculate the change of the honour.
            self_honour = HONOURS_MAPPER.get_honour_by_id(char, 0)
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
            honour_changes[char] = value - self_honour
            total_honours[char] = value

        # Set new honours.
        HONOURS_MAPPER.set_honours(total_honours)

        return honour_changes

                
# main honours handler
HONOURS_HANDLER = HonoursHandler()
