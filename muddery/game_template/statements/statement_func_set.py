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


class ConditionFuncSet(default_set.ConditionFuncSet):
    """
    Statement functions used in conditions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        super(ConditionFuncSet, self).at_creation()

        # self.add(statement_function_class)


class SkillFuncSet(default_set.SkillFuncSet):
    """
    Statement functions used in actions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        super(SkillFuncSet, self).at_creation()

        # self.add(statement_function_class)
