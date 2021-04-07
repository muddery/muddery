"""
Skill handler handles a character's skills.

"""

import random
from muddery.server.combat.combat_runner.base_combat import CStatus


class ChooseSkill(object):
    """
    Choose a skill and the skill's target.
    """
    def choose(self, caller):
        """
        Choose a skill and the skill's target.
        """
        if not caller:
            return

        combat = caller.get_combat()
        if not combat:
            return

        skills = caller.get_available_skills()
        if not skills:
            return

        opponents = combat.get_opponents(caller.id)

        skill = random.choice(skills)
        target = random.choice(opponents)
        return skill.get_element_key(), target
