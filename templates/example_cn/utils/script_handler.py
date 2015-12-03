"""
This model handle scripts.
"""

from muddery.utils.script_handler_base import ScriptHandlerDefault
from muddery.utils import script_actions


class ScriptHandler(ScriptHandlerDefault):
    """
    Loads and handles condition scripts and action scripts.
    """

    def at_handler_creation(self):
        """
        Init script handler, load default scripts.
        """
        super(ScriptHandler, self).at_handler_creation()

        self.add_action("learn_skill", script_actions.learn_skill)
