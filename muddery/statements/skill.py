"""
Default skills.
"""

import random, re
from muddery.utils.localized_strings_handler import _
from muddery.statements.statement_function import StatementFunction


class FuncEscape(StatementFunction):
    """
    Set the caller's attribute.

    Args:
        args[0]: (float) the odds of success escape. Optional, default: 0

    Returns:
        (tuple) message, data
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
            return _("Failed.")

        # send skill's result to the combat handler manually
        # before the handler is removed from the character
        combat_handler.msg_all({"skill_cast": {"caller": self.caller.get_name(),
                                               "target": self.obj.get_name(),
                                               "skill": self.key,
                                               "cast": _("{c%s{n tried to escape.") % self.caller.get_name(),
                                               "result": _("Succeeded!")}})

        combat_handler.skill_escape(self.caller)


class FuncHeal(StatementFunction):
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

        effect = self.args[0]
        if effect <= 0:
            return

        self.obj = self.caller

        # recover caller's hp
        increments = {"hp": int(effect)}
        changes = self.caller.change_status(increments)

        # send skill result
        return _("Healed %s by %d points.") % (self.obj.get_name(), int(changes["hp"]))


class FuncHit(StatementFunction):
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
        # damage = float(self.caller.attack) / (self.caller.attack + self.obj.defence) * self.caller.attack
        damage = round(effect)

        # hurt target
        increments = {"hp": -damage}
        changes = self.obj.change_status(increments)

        # send skill result
        return _("Hit %s by %d points.") % (self.obj.get_name(), int(-changes["hp"]))


class FuncIncreaseMaxHP(StatementFunction):
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
            
        self.obj = self.caller

        # increase max hp
        # recover caller's hp
        increments = {"max_hp": int(effect)}
        changes = self.caller.change_status(increments)

        # increase hp
        increments_hp = {"hp": changes["max_hp"]}
        self.caller.change_status(increments_hp)

        # send skill result
        return _("Raised %s's max HP by %d points.") % (self.obj.get_name(), int(changes["max_hp"]))
