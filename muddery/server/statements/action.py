"""
Actions are used to do somethings.
"""

from django.core.exceptions import ObjectDoesNotExist
from muddery.server.utils.utils import get_object_by_key
from muddery.server.statements.statement_function import StatementFunction


class FuncLearnSkill(StatementFunction):
    """
    Teach the caller a skill.

    Args:
        args[0]: (string) skill's key

    Returns:
        (boolean) learned skill
    """

    key = "learn_skill"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        return self.caller.learn_skill(skill_key, False, False)


class FuncGiveObject(StatementFunction):
    """
    Give some objects to the caller.

    Args:
        args[0]: (string) object's key
        args[1]: (int) object's number. Optional, default: 1

        If only give one args, give only one object to the caller.

    Returns:
        (boolean) Whether all objects accepted.
    """

    key = "give_object"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = 1
        if len(self.args) > 1:
            number = self.args[1]

        obj_list = [{"object": obj_key,
                     "number": number}]

        objects = self.caller.receive_objects(obj_list)
        success = True
        for item in objects:
            if item["reject"]:
                success = False
                break

        return success


class FuncRemoveObjects(StatementFunction):
    """
    Remove some objects from the character.

    Args:
        args[0]: object's key
        args[1]: object's number. Optional, default: 1
    """

    key = "remove_objects"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = 1
        if len(self.args) > 1:
            number = self.args[1]

        return self.caller.remove_object(obj_key, number)


class FuncTeleportTo(StatementFunction):
    """
    Teleport the character to specified room.

    Args:
         args[0]: (string) target room's key

    Returns:
        (boolean) teleport success or not
    """

    key = "teleport_to"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        room_key = self.args[0]
        try:
            destination = get_object_by_key(room_key)
        except ObjectDoesNotExist:
            return False

        return self.caller.move_to(destination)


class FuncFightMob(StatementFunction):
    """
    Fight with specified target.

    Args:
        args[0]: (string) mob's key
        args[1]: (int) mob's level. Optional, default: 1
        args[2]: (string) fight's desc. Optional, default: ""

    Returns:
        (boolean) can fight
    """

    key = "fight_mob"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        mob_key = self.args[0]

        level = 1
        if len(self.args) > 1:
            level = self.args[1]

        desc = ""
        if len(self.args) > 2:
            desc = self.args[2]

        return self.caller.attack_temp_target(mob_key, level, desc)


class FuncFightTarget(StatementFunction):
    """
    Fight with current target.

    Args:
        args[0]: (string) fight's desc. Optional, default: ""

    Returns:
        (boolean) can fight
    """

    key = "fight_target"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.obj:
            return False

        desc = ""
        if self.args:
            desc = self.args[0]

        return self.caller.attack_temp_target(self.obj.get_object_key(), self.obj.get_level(), desc)
        
        
class FuncKillCaller(StatementFunction):
    """
    Kill the caller.

    Returns:
        (boolean) killed
    """
    key = "kill_caller"
    const = False

    def func(self):
        """
        Implement the function.
        """
        self.caller.db.hp = 0
        self.caller.die(None)
        return True
