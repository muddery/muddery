"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

from muddery.server.elements.skill import MudderySkill
from muddery.server.utils.localized_strings_handler import _


class Skill(MudderySkill):
    """
    A skill of the character.
    """
    element_type = "SKILL"

    def do_skill(self, caller, target):
        """
        Do this skill.
        """
        if not self.passive:
            # set mp
            mp = caller.states.load("mp")
            new_mp = mp - self.const.mp
            if new_mp != mp:
                caller.states.save("mp", new_mp)

        return super(Skill, self).do_skill(caller, target)

    def get_available_message(self, caller):
        """
        Check this skill.

        Args:
            caller: (object) the one who cast the skill.

        Returns:
            message: (string) If the skill is not available, returns a string of reason.
                     If the skill is available, return "".
        """
        message = super(Skill, self).get_available_message(caller)
        if message:
            return message
            
        if caller.states.load("mp") < self.const.mp:
            return _("Not enough mana to cast {c%s{n!") % self.get_name()

        return ""

    def is_available(self, caller, passive):
        """
        If this skill is available.

        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            (boolean) available or not.
        """
        result = super(Skill, self).is_available(caller, passive)
        if not result:
            return result
            
        if caller.states.load("mp") < self.const.mp:
            return False

        return True

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(Skill, self).get_appearance(caller)
        
        info["mp"] = self.states.load("mp")

        return info
