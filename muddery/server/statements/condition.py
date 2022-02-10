"""
Condition statements return a boolean value. They can be used in conditional statements.
"""

from muddery.server.statements.statement_function import StatementFunction


class FuncIsQuestAccepted(StatementFunction):
    """
    If the caller has accepted or finished the quest

    Args:
        args[0]: (string) quest's key

    Returns:
        boolean result
    """

    key = "is_quest_accepted"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        quest_key = self.args[0]
        results = [
            self.caller.quest_handler.is_finished(quest_key),
            self.caller.quest_handler.is_in_progress(quest_key),
        ]
        return results[0] or results[1]


class FuncIsQuestAccomplished(StatementFunction):
    """
    All objectives of this quest are accomplished.

    Args:
        args[0]: (string) quest's key

    Returns:
        boolean result
    """

    key = "is_quest_accomplished"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        quest_key = self.args[0]
        return await self.caller.quest_handler.is_accomplished(quest_key)


class FuncIsQuestInProgress(StatementFunction):
    """
    If the caller is doing specified quest.

    Args:
        args[0]: (string) quest's key

    Returns:
        boolean result
    """

    key = "is_quest_in_progress"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        quest_key = self.args[0]
        return self.caller.quest_handler.is_in_progress(quest_key)


class FuncCanProvideQuest(StatementFunction):
    """
    If can provide specified quest to the caller.

    Args:
        args[0]: (string) quest's key

    Returns:
        boolean result
    """

    key = "can_provide_quest"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        quest_key = self.args[0]
        return await self.caller.quest_handler.can_provide(quest_key)


class FuncIsQuestFinished(StatementFunction):
    """
    If specified quest is finished.

    Args:
        args[0]: (string) quest's key

    Returns:
        boolean result
    """

    key = "is_quest_finished"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        quest_key = self.args[0]
        return self.caller.quest_handler.is_finished(quest_key)


class FuncHasObject(StatementFunction):
    """
    If the caller has specified object.

    Args:
        args[0]: (string) object's key

    Returns:
        boolean result
    """

    key = "has_object"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        return self.caller.has_object(obj_key)


class FuncObjectsEqualTo(StatementFunction):
    """
    If the caller has objects equal to the number.

    Args:
        args[0]: (string) object's key
        args[1]: (number) object's number

    Returns:
        boolean result
    """

    key = "obj_equal_to"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args or len(self.args) < 1:
            return False

        obj_key = self.args[0]
        number = self.args[1]

        total = self.caller.total_object_number(obj_key)
        return total == number


class FuncObjectsMoreThan(StatementFunction):
    """
    If the caller has objects more than the number.

    Args:
        args[0]: (string) object's key
        args[1]: (number) object's number

    Returns:
        boolean result
    """

    key = "obj_more_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = self.args[1]

        total = self.caller.total_object_number(obj_key)
        return total > number


class FuncObjectsLessThan(StatementFunction):
    """
    If the caller has objects less than the number.

    Args:
        args[0]: (string) object's key
        args[1]: (number) object's number

    Returns:
        boolean result
    """

    key = "obj_less_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = self.args[1]

        total = self.caller.total_object_number(obj_key)
        return total < number


class FuncHasSkill(StatementFunction):
    """
    If the caller has specified object.

    Args:
        args[0]: (string) skill's key

    Returns:
        boolean result
    """

    key = "has_skill"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]

        return self.caller.get_skill(skill_key) is not None


class FuncSkillEqualTo(StatementFunction):
    """
    If the skill's level equals to the number.

    Args:
        args[0]: (string) skill's key
        args[1]: (number) level

    Returns:
        boolean result
    """

    key = "skill_equal_to"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        level = self.args[1]

        skill = self.caller.get_skill(skill_key)
        if not skill:
            return False

        return await skill.get_level() == level


class FuncSkillMoreThan(StatementFunction):
    """
    If the skill's level more than the number.

    Args:
        args[0]: (string) skill's key
        args[1]: (number) level

    Returns:
        boolean result
    """

    key = "skill_more_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        level = self.args[1]

        skill = self.caller.get_skill(skill_key)
        if not skill:
            return False

        return await skill.get_level() > level


class FuncSkillLessThan(StatementFunction):
    """
    If the skill's level less than the number.

    Args:
        args[0]: (string) skill's key
        args[1]: (number) level

    Returns:
        boolean result
    """

    key = "skill_less_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        level = self.args[1]

        skill = self.caller.get_skill(skill_key)
        if not skill:
            return False

        return await skill.get_level() < level


class FuncAttributeEqualTo(StatementFunction):
    """
    If the caller's attribute equals to the number.

    Args:
        args[0]: (string) attribute's key
        args[1]: (number) number

    Returns:
        boolean result
    """

    key = "attr_equal_to"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        number = self.args[1]

        if await self.caller.states.has(attr_key):
            value = await self.caller.states.get(attr_key)
        elif self.caller.const_data_handler.has(attr_key):
            value = self.caller.const_data_handler.get(attr_key)
        else:
            return

        return value == number


class FuncAttributeMoreThan(StatementFunction):
    """
    If the caller's attribute more than the number.

    Args:
        args[0]: (string) attribute's key
        args[1]: (number) number

    Returns:
        boolean result
    """

    key = "attr_more_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        number = self.args[1]

        if await self.caller.states.has(attr_key):
            value = await self.caller.states.get(attr_key)
        elif self.caller.const_data_handler.has(attr_key):
            value = self.caller.const_data_handler.get(attr_key)
        else:
            return

        return value > number


class FuncAttributeLessThan(StatementFunction):
    """
    If the caller's attribute less than the number.

    Args:
        args[0]: (string) attribute's key
        args[1]: (number) number

    Returns:
        boolean result
    """

    key = "attr_less_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        number = self.args[1]

        if await self.caller.states.has(attr_key):
            value = await self.caller.states.get(attr_key)
        elif self.caller.const_data_handler.has(attr_key):
            value = self.caller.const_data_handler.get(attr_key)
        else:
            return

        return value < number


class FuncRelationshipEqualTo(StatementFunction):
    """
    Check if the caller and the element's relationship equals to the number.

    Args:
        args[0]: (string) element's type
        args[1]: (string) element's key
        args[2]: (number) number

    Returns:
        boolean result
    """

    key = "relation_equal_to"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        element_type = self.args[0]
        element_key = self.args[1]
        number = self.args[2]

        relationship = await self.caller.get_relationship(element_type, element_key)
        if relationship is None:
            return False
        return relationship == number


class FuncRelationshipMoreThan(StatementFunction):
    """
    Check if the caller and the element's relationship is more than the number.

    Args:
        args[0]: (string) element's type
        args[1]: (string) element's key
        args[2]: (number) number

    Returns:
        boolean result
    """

    key = "relation_more_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        element_type = self.args[0]
        element_key = self.args[1]
        number = self.args[2]

        relationship = await self.caller.get_relationship(element_type, element_key)
        if relationship is None:
            return False
        return relationship > number


class FuncRelationshipLessThan(StatementFunction):
    """
    Check if the caller and the element's relationship is less than the number.

    Args:
        args[0]: (string) element's type
        args[1]: (string) element's key
        args[2]: (number) number

    Returns:
        boolean result
    """

    key = "relation_less_than"
    const = True

    async def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        element_type = self.args[0]
        element_key = self.args[1]
        number = self.args[2]

        relationship = await self.caller.get_relationship(element_type, element_key)
        if relationship is None:
            return False
        return relationship < number
