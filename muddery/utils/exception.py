"""
Define custom exception.
"""

class MudderyError(Exception):
    """
    Define custom exception.
    """
    def __init__(self, value):
        super(MudderyError, self).__init__(value)
        self.value = value

    def __str__(self):
        return repr(self.value)
