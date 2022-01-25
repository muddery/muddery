"""
Actions are used to do somethings.
"""

import traceback
from muddery.server.statements.statement_function import StatementFunction
from muddery.server.server import Server
from muddery.server.utils.logger import logger


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

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        skill_level = self.args[1] if len(self.args) > 1 else 0
        try:
            self.caller.learn_skill(skill_key, skill_level, False)
            return True
        except:
            return False


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

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = 1
        if len(self.args) > 1:
            number = self.args[1]

        obj_list = [{"object_key": obj_key,
                     "number": number}]

        objects = await self.caller.receive_objects(obj_list)
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

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = 1
        if len(self.args) > 1:
            number = self.args[1]

        return self.caller.remove_objects_by_key(obj_key, number)


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

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        room_key = self.args[0]
        try:
            destination = Server.world.get_room(room_key)
        except KeyError:
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

    async def func(self):
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

        return await self.caller.attack_temp_target(mob_key, level, desc)


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

    async def func(self):
        """
        Implement the function.
        """
        if not self.obj:
            return False

        desc = ""
        if self.args:
            desc = self.args[0]

        return await self.caller.attack_temp_target(self.obj.get_element_key(), await self.obj.get_level(), desc)


class FuncSetRelationship(StatementFunction):
    """
    Set the relationship between the player and the element.

    Args:
        args[0]: (string) element's type
        args[1]: (string) element's key
        args[2]: (number) number

    Returns:
        (boolean) value has set
    """

    key = "set_relation"
    const = False

    async def func(self):
        """
        Implement the function.
        """
        element_type = self.args[0]
        element_key = self.args[1]
        number = self.args[2]

        try:
            await self.caller.set_relationship(element_type, element_key, number)
            return True
        except:
            traceback.print_exc()
            logger.log_trace("Set relationship error.")
            return False


class FuncAddRelationship(StatementFunction):
    """
    Change the relationship between the player and the element.

    Args:
        args[0]: (string) element's type
        args[1]: (string) element's key
        args[2]: (number) number

    Returns:
        (boolean) value has set
    """

    key = "inc_relation"
    const = False

    async def func(self):
        """
        Implement the function.
        """
        element_type = self.args[0]
        element_key = self.args[1]
        number = self.args[2]

        try:
            await self.caller.increase_relationship(element_type, element_key, number)
            return True
        except:
            traceback.print_exc()
            logger.log_trace("Set relationship error.")
            return False