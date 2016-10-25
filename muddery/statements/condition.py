"""
Condition statements return a boolean value. They can be used in conditional statements.
"""


from muddery.statements.statement_function import StatementFunction


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


class FuncIsQuestCompleted(StatementFunction):
    """
    If specified quest is completed.

    Args:
        args[0]: (string) quest's key

    Returns:
        boolean result
    """

    key = "is_quest_completed"
    const = True

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        quest_key = self.args[0]
        return self.caller.quest_handler.is_completed(quest_key)


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
