"""
Condition statements return a boolean value. They can be used in conditional statements.
"""

from muddery.server.statements.statement_function import StatementFunction


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

    def func(self):
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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        quest_key = self.args[0]
        return self.caller.quest_handler.can_provide(quest_key)


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

    def func(self):
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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]

        for item in self.caller.contents:
            if item.get_data_key() == obj_key:
                return True
        return False


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

    def func(self):
        """
        Implement the function.
        """
        if not self.args or len(self.args) < 1:
            return False

        obj_key = self.args[0]
        number = self.args[1]

        total = 0
        for item in self.caller.contents:
            if item.get_data_key() == obj_key:
                total += item.get_number()
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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = self.args[1]

        total = 0
        for item in self.caller.contents:
            if item.get_data_key() == obj_key:
                total += item.get_number()
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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        obj_key = self.args[0]
        number = self.args[1]

        total = 0
        for item in self.caller.contents:
            if item.get_data_key() == obj_key:
                total += item.get_number()
        return total < number


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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        level = self.args[1]

        if skill_key not in self.caller.db.skills:
            return False

        skill = self.caller.db.skills[skill_key]
        return skill.level == level


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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        level = self.args[1]

        if skill_key not in self.caller.db.skills:
            return False

        skill = self.caller.db.skills[skill_key]
        return skill.level > level


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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        skill_key = self.args[0]
        level = self.args[1]

        if skill_key not in self.caller.db.skills:
            return False

        skill = self.caller.db.skills[skill_key]
        return skill.level < level


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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        number = self.args[1]

        if not self.caller.custom_properties_handler.has(attr_key):
            return False

        value = getattr(self.caller.prop, attr_key)
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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        number = self.args[1]

        if not self.caller.custom_properties_handler.has(attr_key):
            return False

        value = getattr(self.caller.prop, attr_key)
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

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        number = self.args[1]

        if not self.caller.custom_properties_handler.has(attr_key):
            return False

        value = getattr(self.caller.prop, attr_key)
        return value < number
