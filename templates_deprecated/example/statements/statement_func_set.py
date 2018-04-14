"""
Default statement functions.
"""

from muddery.statements.statement_func_set import BaseStatementFuncSet
import muddery.statements.skill as default_skill
import statements.skill as skill


class SkillFuncSet(BaseStatementFuncSet):
    """
    Statement functions used in actions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        self.add(default_skill.FuncEscape)
        self.add(default_skill.FuncHeal)
        self.add(default_skill.FuncIncreaseMaxHP)
        
        self.add(skill.FuncHit)
