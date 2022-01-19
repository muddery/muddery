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

    async def do_skill(self, caller, target):
        """
        Do this skill.
        """
        if not self.passive:
            # set mp
            mp = await caller.states.load("mp")
            new_mp = mp - self.const.mp
            if new_mp != mp:
                await caller.states.save("mp", new_mp)

        return await super(Skill, self).do_skill(caller, target)

    async def is_available(self, caller, passive):
        """
        If this skill is available.

        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            (boolean) available or not.
        """
        result = await super(Skill, self).is_available(caller, passive)
        if not result:
            return result
            
        if await caller.states.load("mp") < self.const.mp:
            return False

        return True

    def get_mp(self):
        """
        Get skill's mp.
        :return:
        """
        return self.const.mp

    def get_appearance(self):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(Skill, self).get_appearance()
        info["mp"] = self.const.mp

        return info
