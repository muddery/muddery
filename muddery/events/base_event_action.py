"""
Event action's base class.
"""

class BaseEventAction(object):
    """
    Event action's base class.
    """
    key = ""
    name = ""

    def func(self, event, character):
        """
        Event action's function.
        """
        pass

