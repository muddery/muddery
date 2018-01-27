"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

from muddery.typeclasses.character_skills import MudderySkill
from muddery.utils.localized_strings_handler import _


class Skill(MudderySkill):
    """
    A skill of the character.
    """
    def after_data_loaded(self):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(Skill, self).after_data_loaded()

        # set data
        self.mp = getattr(self.dfield, "mp", "")

    def do_skill(self, target):
        """
        Do this skill.
        """
        if not self.passive:
            # set mp
            self.db.owner.db.mp -= self.mp

        return super(Skill, self).do_skill(target)

    def check_available(self, passive):
        """
        Check this skill.

        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            message: (string) If the skill is not available, returns a string of reason.
                     If the skill is available, return "".
        """
        message = super(Skill, self).check_available(passive)
        if message:
            return message
            
        if self.db.owner.db.mp < self.mp:
            return _("Not enough mana to cast {c%s{n!") % self.get_name()

        return ""

    def is_available(self, passive):
        """
        If this skill is available.

        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            (boolean) available or not.
        """
        result = super(Skill, self).is_available(passive)
        if not result:
            return result
            
        if self.db.owner.db.mp < self.mp:
            return False

        return True

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(Skill, self).get_appearance(caller)
        
        info["mp"] = self.mp

        return info