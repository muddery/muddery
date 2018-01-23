"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

import time
from django.conf import settings
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.utils import get_class


class Skill(get_class("CLASS_SKILL")):
    """
    A skill of the character.
    """
    def after_data_loaded(self):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(MudderySkill, self).after_data_loaded()

        # set data
        self.function = getattr(self.dfield, "function", "")
        self.cd = getattr(self.dfield, "cd", 0)
        self.passive = getattr(self.dfield, "passive", False)
        self.message = getattr(self.dfield, "message", "")
        self.main_type = getattr(self.dfield, "main_type", "")
        self.sub_type = getattr(self.dfield, "sub_type", "")
        self.mp = getattr(self.dfield, "mp", "")

    def check_available(self):
        """
        Check this skill.

        Returns:
            message: (string) If the skill is not available, returns a string of reason.
                     If the skill is available, return "".
        """
        message = super(Skill, self).check_available()
        if message:
            return message
            
        if self.owner.mp < self.mp:
            return _("Not enough mana to cast {c%s{n!") % self.get_name()

        return ""

    def is_available(self):
        """
        If this skill is available.
        """
        result = super(Skill, self).is_available()
        if not result:
            return result
            
        if self.owner.mp < self.mp:
            return False

        return True
