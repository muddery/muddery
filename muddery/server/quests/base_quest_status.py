"""
Quest dependency's base class.
"""

class BaseQuestStatus(object):
    """
    Quest status's base class.
    """
    key = ""
    name = ""

    def match(self, caller, quest_key):
        """
        If the quest matches status.
        """
        return True
 
