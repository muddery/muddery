"""
Default skills.
"""

from muddery.server.utils.localized_strings_handler import _
from muddery.server.statements.statement_function import StatementFunction


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

        target_name = self.obj.get_name()

        # calculate the damage
        damage = float(self.caller.const.attack) / (self.caller.const.attack + self.obj.const.defence) * self.caller.const.attack
        damage = round(damage * effect)

        # hurt target
        hp = self.obj.states.load("hp")
        new_hp = self.obj.validate_property("hp", hp - damage)
        if new_hp != hp:
            self.obj.states.save("hp", new_hp)

        # send skill result
        return _("Hit %s by %d points.") % (target_name, hp - new_hp)


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
        heal = int(effect)

        # hurt target
        hp = self.obj.states.load("hp")
        new_hp = self.obj.validate_property("hp", hp + heal)
        if new_hp != hp:
            self.obj.states.save("hp", new_hp)

        # send skill result
        return _("Healed %s by %d points.") % (self.obj.get_name(), new_hp - hp)


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
        increase = int(effect)
        if increase > 0:
            max_hp = self.obj.const.max_hp
            new_max_hp = max_hp + increase
            if new_max_hp != max_hp:
                self.obj.const_data_handler.add("max_hp", new_max_hp)

            # increase hp
            hp = self.obj.states.load("hp")
            new_hp = self.obj.validate_property("hp", hp + increase)
            if new_hp != hp:
                self.caller.states.save("hp", new_hp)

        # send skill result
        return _("Raised %s's max HP by %d points.") % (self.obj.get_name(), increase)
