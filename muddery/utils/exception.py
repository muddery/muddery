"""
Define custom exception.
"""

class MudderyError(Exception):
    """
    Define custom exception.
    
    MudderyError(<Error Message>) or
    MudderyError(<Error Code>, <Error Message>, data=<Error Data>)
    """
    def __init__(self, *args, **kwargs):
        self.code = -1
        self.data = None

        if len(args) == 0:
            super(MudderyError, self).__init__()
        elif len(args) == 1:
            super(MudderyError, self).__init__(args[0])
        else:
            super(MudderyError, self).__init__(args[1])
            self.code = args[0]
            self.data = kwargs.get("data")


class ERR(object):
    """
    Error codes.
    """
    no_error = 0

    unknown = -1

    internal = 10000

    no_api = 10001

    no_authentication = 10002

    no_permission = 10003

    missing_args = 10004

    no_table = 10005

    invalid_form = 10006


