"""
Default statement functions.
"""

from muddery.server.statements.statement_func_set import BaseStatementFuncSet
import muddery.server.statements.action as action
import muddery.server.statements.condition as condition
import muddery.server.statements.attribute as attribute
import muddery.server.statements.rand as rand
import muddery.server.statements.skill as skill


class ActionFuncSet(BaseStatementFuncSet):
    """
    Statement functions used in actions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        self.add(attribute.FuncSetAttr)
        self.add(attribute.FuncRemoveAttr)

        self.add(action.FuncLearnSkill)
        self.add(action.FuncGiveObject)
        self.add(action.FuncRemoveObjects)
        self.add(action.FuncTeleportTo)
        self.add(action.FuncFightMob)
        self.add(action.FuncFightTarget)
        self.add(action.FuncKillCaller)


class ConditionFuncSet(BaseStatementFuncSet):
    """
    Statement functions used in conditions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        self.add(condition.FuncIsQuestInProgress)
        self.add(condition.FuncCanProvideQuest)
        self.add(condition.FuncIsQuestFinished)
        self.add(condition.FuncHasObject)
        self.add(condition.FuncObjectsEqual)
        self.add(condition.FuncObjectsMoreThan)
        self.add(condition.FuncObjectsLessThan)
        self.add(condition.FuncSkillMoreThan)
        self.add(condition.FuncAttributeMoreThan)
        self.add(condition.FuncAttributeLessThan)

        self.add(attribute.FuncGetAttr)
        self.add(attribute.FuncHasAttr)
        self.add(attribute.FuncCheckAttr)

        self.add(rand.FuncOdd)
        self.add(rand.FuncRand)
        self.add(rand.FuncRandInt)


class SkillFuncSet(BaseStatementFuncSet):
    """
    Statement functions used in actions.
    """
    def at_creation(self):
        """
        Load statement functions here.
        """
        self.add(skill.FuncEscape)
        self.add(skill.FuncHeal)
        self.add(skill.FuncHit)
        self.add(skill.FuncIncreaseMaxHP)
