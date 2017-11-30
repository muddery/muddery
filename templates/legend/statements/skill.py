"""
Default skills.
"""

from muddery.utils.localized_strings_handler import _
from muddery.statements.skill import SkillFunction


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
        damage = float(self.caller.cattr.attack) / (self.caller.cattr.attack + self.obj.cattr.defence) * self.caller.cattr.attack
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
