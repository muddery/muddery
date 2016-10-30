"""
Custom statement functions.
"""

from muddery.statements import default_statement_func_set as default_set


class ActionFuncSet(default_set.ActionFuncSet):
    """
    Custom statement functions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        super(ActionFuncSet, self).at_creation()

        # self.add(statement_function_class)
