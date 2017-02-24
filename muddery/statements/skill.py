"""
Default skills.
"""

import random
from muddery.utils.localized_strings_handler import LS


from muddery.statements.statement_function import SkillFunction


class FuncEscape(SkillFunction):
    """
    Set the caller's attribute.

    Args:
        args[0]: (float) the odds of success escape. Optional, default: 0

    Returns:
        None
    """

    key = "escape"
    const = False

    def func(self):
        """
        Implement the function.
        """
        combat_handler = self.caller.ndb.combat_handler
        if not combat_handler:
            # caller is not in combat.
            return

        self.obj = self.caller

        odd = 0.0
        if self.args:
            odd = self.args[0]

        rand = random.random()
        if rand >= odd:
            # escape failed
            result = self.result_message(effect=0, message_model=LS("%(c)s tried to escape, but failed."))
            self.caller.send_skill_result(result)
            return

        # send skill's result to the combat handler manually
        # before the handler is removed from the character
        result = self.result_message(effect=1, message_model=LS("%(c)s tried to escape. Succeeded!"))
        self.caller.send_skill_result(result)

        combat_handler.skill_escape(self.caller)


class FuncHeal(SkillFunction):
    """
    Heal the caller.

    Args:
        args[0]: (int) the hp value to increase.

    Returns:
        None
    """

    key = "heal"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return

        self.obj = self.caller

        hp = self.args[0]
        message = getattr(self.kwargs, "message", "")

        # recover caller's hp
        recover_hp = int(hp)

        if self.caller.db.hp < 0:
            self.caller.db.hp = 0

        if self.caller.db.hp + recover_hp > self.caller.max_hp:
            recover_hp = self.caller.max_hp - self.caller.db.hp

        # add actual hp value
        if recover_hp > 0:
            self.caller.db.hp += recover_hp
            self.caller.show_status()

        # character's status after skill casted
        status = [{"dbref": self.caller.dbref,
                   "max_hp": self.caller.max_hp,
                   "hp": self.caller.db.hp}]

        # send skill result
        result = self.result_message(effect=int(hp), status=status)
        self.caller.send_skill_result(result)


class FuncHit(SkillFunction):
    """
    Hit the target.

    Args:
        args[0]: (int) the ratio of the damage.

    Returns:
        None
    """
    key = "hit"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return

        effect = self.args[0]
        if effect <= 0:
            return

        if not self.obj:
            return

        # calculate the damage
        damage = float(self.caller.attack) / (self.caller.attack + self.obj.defence) * self.caller.attack
        damage = round(damage * effect)

        # hurt target
        self.obj.db.hp -= damage
        if self.obj.db.hp < 0:
            self.obj.db.hp = 0

        self.obj.show_status()

        # character's status after skill casted
        status = [{"dbref": self.obj.dbref,
                   "max_hp": self.obj.max_hp,
                   "hp": self.obj.db.hp}]

        # send skill result
        result = self.result_message(effect=int(damage), status=status)
        self.caller.send_skill_result(result)


class FuncIncreaseMaxHP(SkillFunction):
    """
    Passive skill, increase the caller's max_hp.

    Args:
        args[0]: (int) the max_hp value to increase.

    Returns:
        None
    """
    key = "max_hp"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return

        effect = self.args[0]
        if effect <= 0:
            return

        # increase max hp
        self.caller.max_hp += effect

        # increase hp
        hp = self.caller.db.hp + effect
        if hp > self.caller.max_hp:
            hp = self.caller.max_hp
        self.caller.db.hp = hp

        # character's status after skill casted
        status = [{"dbref": self.caller.dbref}]

        # send skill result
        result = self.result_message(effect=effect, status=status)
        self.caller.send_skill_result(result)
