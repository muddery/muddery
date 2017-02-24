"""
Base statement function.
"""


class StatementFunction(object):
    """
    This is the base statement function class.

    Args:
        args[0]: statement function's args

    Returns:
        return value
    """

    # the function's key
    key = "statement_function"

    # If this function may change the caller's status, const is False
    # only const functions can be used in conditions.
    const = False

    def __init__(self):
        """
        Init default attributes.
        """
        self.caller = None
        self.obj = None
        self.args = None
        self.kwargs = None

    def set(self, caller, obj, args, **kwargs):
        """
        Set function args.
        """
        self.caller = caller
        self.obj = obj
        self.args = args
        self.kwargs = kwargs

    def func(self):
        """
        Implement the function.
        """
        pass


class SkillFunction(StatementFunction):
    """
    This is the base skill function class.
    """
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
        self.message_model = kwargs.get("message", "")
        
    def result_message(self, effect=None, message_model=None):
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

        if self.message_model:
            values = {"n": self.name,
                      "c": caller_name,
                      "o": obj_name,
                      "e": effect_str}
            message = self.message_model % values

        return {"key": self.key,             # skill's key
                "name": self.name,           # skill's name
                "effect": effect,            # skill's effect
                "message": message,          # skill's message
                "caller": caller_dbref,      # caller's dbref
                "target": obj_dbref}         # target's dbref
