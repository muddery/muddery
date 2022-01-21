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

    async def func(self):
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

        # hit the target
        changed = await self.obj.change_state("hp", -damage)

        # send skill result
        return _("Hit %s by %d points.") % (target_name, -changed)


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

    async def func(self):
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

        # heal the target
        changed = await self.obj.change_state("hp", heal)

        # send skill result
        return _("Healed %s by %d points.") % (self.obj.get_name(), changed)


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

    async def func(self):
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
        changed = 0

        if increase > 0:
            changed = await self.obj.change_const_property("max_hp", increase)

            # increase hp
            await self.obj.change_state("hp", changed)

        # send skill result
        return _("Raised %s's max HP by %d points.") % (self.obj.get_name(), changed)
