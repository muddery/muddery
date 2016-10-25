"""
Random statements can return a random result.
"""

import random
from muddery.statements.statement_function import StatementFunction


class FuncOdd(StatementFunction):
    """
    If a random number matches the odd.

    Args:
        args[0]: (float) an odd number between 0 and 1

    Returns:
        boolean result
    """

    key = "odd"
    const = True

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        odd = self.args[0]
        return random.random() < odd


class FuncRand(StatementFunction):
    """
    Get a random number.

    Args:
        args[0]: (float) the bound of the random number
        args[1]: (float) the bound of the random number. Optional

    Returns:
        (float) a random number between args[0] and args[1]

        If only give one args, the random number will between 0 and args[0]
    """

    key = "rand"
    const = True

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return 0

        bound1 = self.args[0]
        bound2 = 0
        if len(self.args) > 1:
            bound2 = self.args[1]

        return random.uniform(bound1, bound2)


class FuncRandInt(StatementFunction):
    """
    Get a random integer number.

    Args:
        args[0]: (int) the bound of the random number
        args[1]: (int) the bound of the random number. Optional

    Returns:
        (int) a random number between args[0] and args[1]

        If only give one args, the random number will between 0 and args[0].
    """

    key = "randint"
    const = True

    def func(self):
        """
        Implement the function.
        """

        if not self.args:
            return 0

        bound1 = self.args[0]
        bound2 = 0
        if len(self.args) > 1:
            bound2 = self.args[1]

        return random.randint(bound1, bound2)
