"""
Custom statement functions.
"""

from muddery.statements.default_statement_func_set import DefaultStatementFuncSet


class StatementFuncSet(DefaultStatementFuncSet):
    """
    Custom statement functions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        super(StatementFuncSet, self).at_creation()

        # self.add(statement_function_class)
