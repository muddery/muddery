"""
Base statement function.
"""


class StatementFunction(object):
    """
    This is the base statement function class.

    Args:
        args[0]: statement function's args

    Returns:
        return value
    """

    # the function's key
    key = "statement_function"

    # If this function may change the caller's status, const is False
    # only const functions can be used in conditions.
    const = False

    def __init__(self):
        """
        Init default attributes.
        """
        self.caller = None
        self.obj = None
        self.args = None
        self.kwargs = None

    def set(self, caller, obj, args, **kwargs):
        """
        Set function args.
        """
        self.caller = caller
        self.obj = obj
        self.args = args
        self.kwargs = kwargs

    def func(self):
        """
        Implement the function.
        """
        pass
