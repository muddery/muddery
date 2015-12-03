"""
This model handle scripts.
"""

from muddery.utils.script_handler_base import ScriptHandlerDefault


class ScriptHandler(ScriptHandlerDefault):
    """
    Loads and handles condition scripts and action scripts.
    """

    def at_handler_creation(self):
        """
        Init script handler, load default scripts.
        """
        super(ScriptHandler, self).at_handler_creation()

        # self.add_condition("condition_key", condition_func)
        # self.add_action("action_key", action_func)
