"""
Default skills.
"""

import random, re
from muddery.utils.localized_strings_handler import _


from muddery.statements.statement_function import StatementFunction


class SkillFunction(StatementFunction):
    """
    This is the base skill function class.
    """
    msg_escape = re.compile(r'%[%|n|c|t|e]')

    @staticmethod
    def escape_fun(word):
        """
        Change escapes to target words.
        """
        escape_word = word.group()
        char = escape_word[1]
        if char == "%":
            return char
        else:
            return "%(" + char + ")s"

    def __init__(self):
        """
        Init default attributes.
        """
        super(SkillFunction, self).__init__()

        # skill's name
        self.name = None

        # skill's result message model
        self.message_model = None

    def set(self, caller, obj, args, **kwargs):
        """
        Set function args.
        """
        super(SkillFunction, self).set(caller, obj, args, **kwargs)

        self.key = kwargs.get("key", "")
        self.name = kwargs.get("name", "")
        message_model = kwargs.get("message", "")
        self.message_model = self.msg_escape.sub(self.escape_fun, message_model)

    def result_message(self, effect=None, status=None, message_model=None):
        """
        Create skill's result message.
        """
        caller_name = ""
        caller_dbref = ""
        obj_name = ""
        obj_dbref = ""
        effect_str = ""
        message = ""

        if self.caller:
            caller_name = self.caller.get_name()
            caller_dbref = self.caller.dbref

        if self.obj:
            obj_name = self.obj.get_name()
            obj_dbref = self.obj.dbref

        if effect:
            effect_str = str(effect)

        if message_model is None:
            message_model = self.message_model

        if message_model:
            values = {"n": self.name,
                      "c": caller_name,
                      "t": obj_name,
                      "e": effect_str}
            message = message_model % values

        return {"key": self.key,            # skill's key
                "name": self.name,          # skill's name
                "effect": effect,           # skill's effect
                "status": status,           # character's status
                "message": message,         # skill's message
                "caller": caller_dbref,     # caller's dbref
                "target": obj_dbref}        # target's dbref


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
            result = self.result_message(effect=0, message_model=_("%(c)s tried to escape, but failed."))
            self.caller.send_skill_result(result)
            return

        # send skill's result to the combat handler manually
        # before the handler is removed from the character
        result = self.result_message(effect=1, message_model=_("%(c)s tried to escape. Succeeded!"))
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
        # damage = float(self.caller.attack) / (self.caller.attack + self.obj.defence) * self.caller.attack
        damage = round(effect)

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
        status = [{"dbref": self.caller.dbref,
                   "max_hp": self.caller.max_hp,
                   "hp": self.caller.db.hp}]

        # send skill result
        result = self.result_message(effect=effect, status=status)
        self.caller.send_skill_result(result)
