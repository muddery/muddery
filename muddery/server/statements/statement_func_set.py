"""
A statement function set holds a set of statement functions that can be used in statements.
"""


class BaseStatementFuncSet(object):
    """
    A statement function set holds a set of statement functions that can be used in statements.
    """

    def __init__(self):
        self.funcs = {}
        self.at_creation()

    def at_creation(self):
        """
        Load statement functions here.
        """
        pass

    def add(self, func_cls):
        """
        Add a statement function's class.

        Args:
            func_cls: statement function's class

        Returns:
            None
        """
        # save an instance of the function class
        self.funcs[func_cls.key] = func_cls

    def get_func_class(self, key):
        """
        Get statement function's class.

        Args:
            key: statement function's key.

        Returns:
            function's class
        """
        if key in self.funcs:
            return self.funcs[key]
        else:
            return None
