"""
Default statement functions.
"""

from muddery.statements.statement_func_set import BaseStatementFuncSet
import muddery.statements.action as action
import muddery.statements.condition as condition
import muddery.statements.attribute as attribute
import muddery.statements.rand as rand


class DefaultStatementFuncSet(BaseStatementFuncSet):
    """
    Default statement functions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        self.add(condition.FuncIsQuestInProgress)
        self.add(condition.FuncCanProvideQuest)
        self.add(condition.FuncIsQuestCompleted)
        self.add(condition.FuncHasObject)

        self.add(attribute.FuncGetAttr)
        self.add(attribute.FuncHasAttr)
        self.add(attribute.FuncCheckAttr)
        self.add(attribute.FuncSetAttr)
        self.add(attribute.FuncRemoveAttr)

        self.add(rand.FuncOdd)
        self.add(rand.FuncRand)
        self.add(rand.FuncRandInt)

        self.add(action.FuncLearnSkill)
        self.add(action.FuncGiveObject)
        self.add(action.FuncRemoveObjects)
        self.add(action.FuncTeleportTo)
        self.add(action.FuncFightMob)
        self.add(action.FuncFightTarget)
