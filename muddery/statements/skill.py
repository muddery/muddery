"""
Default skills.
"""

import random
from muddery.utils.localized_strings_handler import LS


from muddery.statements.statement_function import StatementFunction


class FuncEscape(StatementFunction):
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

        odd = 0.0
        if self.args:
            odd = self.args[0]

        rand = random.random()
        if rand >= odd:
            # escape failed
            result = {"type": "escape",
                      "message": [LS("%s tried to escape, but failed.") % self.caller.get_name()],
                      "caller": self.caller.dbref,
                      "success": False}
            self.caller.skill_results([result])
            return

        # send skill's result to the combat handler manually
        # before the handler is removed from the character
        result = {"type": "escape",
                  "message": [LS("%s tried to escape. And succeeded!") % self.caller.get_name()],
                  "caller": self.caller.dbref,
                  "success": True}
        self.caller.skill_results([result])

        combat_handler.remove_character(self.caller)
        if combat_handler.can_finish():
            combat_handler.finish()

        self.caller.msg({"combat_finish": {"escaped": True}})


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

        recover_hp = self.obj.add_hp(effect)
        if recover_hp > 0:
            self.obj.show_status()

        result = {"type": "healed",                 # heal result
                  "message": [LS("%s healed %s HPs.") % (self.obj.get_name(), int(effect))],
                  "caller": self.caller.dbref,      # caller's dbref
                  "target": self.obj.dbref,         # target's dbref
                  "effect": effect,                 # effect
                  "hp": self.obj.db.hp,             # current hp of the target
                  "max_hp": self.obj.max_hp}        # max hp of the target

        self.caller.skill_results([result])


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
        damage = float(self.caller.attack) / (self.caller.attack + self.obj.defence) * self.caller.attack
        damage = round(damage * effect)

        # hurt target
        self.obj.hurt(damage)

        result = {"type": "attacked",               # attack result
                  "message": [LS("%s hitted %s.") % (self.caller.get_name(), self.obj.get_name()),
                              LS("%s lost %s HPs.") % (self.obj.get_name(), int(damage))],
                  "caller": self.caller.dbref,      # caller's dbref
                  "target": self.obj.dbref,         # target's dbref
                  "effect": damage,                 # effect
                  "hp": self.obj.db.hp,             # current hp of the target
                  "max_hp": self.obj.max_hp}        # max hp of the target

        self.caller.skill_results([result])


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

        # increase max hp
        self.caller.max_hp += effect

        # increase hp
        hp = self.caller.db.hp + effect
        if hp > self.caller.max_hp:
            hp = self.caller.max_hp
        self.caller.db.hp = hp
