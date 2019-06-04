"""
Default skills.
"""

from muddery.utils.localized_strings_handler import _
from muddery.statements.statement_function import StatementFunction


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
        damage = float(self.caller.prop.attack) / (self.caller.prop.attack + self.obj.prop.defence) * self.caller.prop.attack
        damage = round(damage * effect)

        # hurt target
        increments = {"hp": -damage}
        changes = self.obj.change_properties(increments)

        # send skill result
        return _("Hit %s by %d points.") % (self.obj.get_name(), int(-changes["hp"]))

