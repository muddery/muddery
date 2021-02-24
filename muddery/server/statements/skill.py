"""
Default skills.
"""

import random
from muddery.server.utils.localized_strings_handler import _
from muddery.server.statements.statement_function import StatementFunction


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

        combat_handler.escape_combat(self.caller)
        return _("Succeeded!")
