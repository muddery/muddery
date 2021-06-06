"""
Skill handler handles a character's skills.

"""

import random
from muddery.server.combat.combat_runner.base_combat import CStatus


class ChooseSkill(object):
    """
    Choose a skill and the skill's target.
    """
    type_attack = "ATTACK"
    type_heal = "HEAL"

    def choose(cls, caller):
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

        hp = caller.states.load("hp")
        max_hp = caller.const.max_hp
        if hp < max_hp / 2:
            # heal self
            heal_skills = [skill for skill in skills if skill.main_type == cls.type_heal]
            if not heal_skills and hp < max_hp / 4:
                heal_skills = [skill for skill in skills if skill.sub_type == cls.type_heal]
                
            if heal_skills:
                skill = random.choice(heal_skills)
                target_id = caller.get_id()
                return skill.get_element_key(), target_id

        opponents = combat.get_opponents(caller.get_id())
        if opponents:
            # attack opponents
            attack_skills = [skill for skill in skills if skill.main_type == cls.type_attack]
            if not attack_skills:
                attack_skills = [skill for skill in skills if skill.sub_type == cls.type_attack]

            if attack_skills:
                skill = random.choice(attack_skills)

                # find the lowest hp
                sorted_opponents = sorted(opponents, key=lambda t: t.states.load("hp"))
                target_id = sorted_opponents[0].get_id()
                return skill.get_element_key(), target_id

        return
