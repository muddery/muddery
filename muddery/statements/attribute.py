"""
Set or get caller's attrubutes.
"""


from muddery.statements.statement_function import StatementFunction


class FuncSetAttr(StatementFunction):
    """
    Set the caller's attribute.

    Args:
        args[0]: (string) attribute's key
        args[1]: attribute value. Optional, default: None

    Returns:
        (boolean) can set attribute
    """

    key = "set_attr"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        value = None
        if len(self.args) > 1:
            value = self.args[1]

        self.caller.statement_attr.set(attr_key, value)
        return True


class FuncGetAttr(StatementFunction):
    """
    Get the caller's attribute.

    Args:
        args[0]: (string) attribute's key
        args[1]: default value if the caller does not have this attribute. Optional, default: None

    Returns:
        Attribute's value
    """

    key = "get_attr"
    const = True

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return None

        key = self.args[0]
        default = None
        if len(self.args) > 1:
            default = self.args[1]

        return self.caller.statement_attr.get(key, default)


class FuncRemoveAttr(StatementFunction):
    """
    Remove the caller's attribute.

    Args:
        args[0]: (string) attribute's key

    Returns:
        (boolean) remove success
    """

    key = "remove_attr"
    const = False

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        key = self.args[0]
        return self.caller.statement_attr.remove(key)


class FuncHasAttr(StatementFunction):
    """
    Does this attribute exist.

    Args:
        args[0]: (string) attribute key

    Returns:
        boolean result
    """

    key = "has_attr"
    const = True

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]
        return self.caller.statement_attr.has(attr_key)


class FuncCheckAttr(StatementFunction):
    """
    Does this attribute match the value.

    Args:
        args[0]: (string) attribute's key
        args[1]: attribute's value

        If only give one args, it works the same as FuncHasAttr.

    Returns:
        boolean result
    """

    key = "check_attr"
    const = True

    def func(self):
        """
        Implement the function.
        """
        if not self.args:
            return False

        attr_key = self.args[0]

        if len(self.args) < 2:
            return self.caller.statement_attr.has(attr_key)
        else:
            value = self.args[1]
            return self.caller.statement_attr.check_value(attr_key, value)
