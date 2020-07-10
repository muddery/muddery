"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

from muddery.server.typeclasses.skill import MudderySkill
from muddery.server.utils.localized_strings_handler import _


class Skill(MudderySkill):
    """
    A skill of the character.
    """
    typeclass_key = "SKILL"

    def do_skill(self, target):
        """
        Do this skill.
        """
        if not self.passive:
            # set mp
            self.owner.prop.mp -= self.prop.mp

        return super(Skill, self).do_skill(target)

    def check_available(self):
        """
        Check this skill.

        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            message: (string) If the skill is not available, returns a string of reason.
                     If the skill is available, return "".
        """
        message = super(Skill, self).check_available()
        if message:
            return message
            
        if self.owner.prop.mp < self.prop.mp:
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
            
        if self.owner.prop.mp < self.prop.mp:
            return False

        return True

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(Skill, self).get_appearance(caller)
        
        info["mp"] = self.prop.mp

        return info
