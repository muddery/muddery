"""
Define custom exception.
"""

class MudderyError(Exception):
    """
    Define custom exception.
    
    MudderyError(<Error Message>) or
    MudderyError(<Error Code>, <Error Message>)
    """
    def __init__(self, *args):
        self.code = -1

        if len(args) == 0:
            super(MudderyError, self).__init__()
        elif len(args) == 1:
            super(MudderyError, self).__init__(args[0])
        else:
            super(MudderyError, self).__init__(args[1])
            self.code = args[0]
