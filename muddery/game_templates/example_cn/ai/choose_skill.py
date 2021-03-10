"""
Skill handler handles a character's skills.

"""

import random
from muddery.server.combat.base_combat_handler import CStatus


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
        
        combat = caller.ndb.combat_handler
        if not combat:
            return

        skills = caller.get_available_skills()
        if not skills:
            return

        team = caller.get_team()
        chars = combat.get_combat_characters()
        # teammates = [c for c in characters if c.get_team() == team]
        opponents = [c["char"] for c in chars if c["status"] == CStatus.ACTIVE and c["char"].get_team() != team]

        hp = caller.states.load("hp")
        max_hp = caller.const.max_hp
        if hp < max_hp / 2:
            # heal self
            heal_skills = [skill for skill in skills if skill.main_type == cls.type_heal]
            if not heal_skills and hp < max_hp / 4:
                heal_skills = [skill for skill in skills if skill.sub_type == cls.type_heal]
                
            if heal_skills:
                skill = random.choice(heal_skills)
                target = caller
                return skill.get_element_key(), target
        
        if opponents:
            # attack opponents
            attack_skills = [skill for skill in skills if skill.main_type == cls.type_attack]
            if not attack_skills:
                attack_skills = [skill for skill in skills if skill.sub_type == cls.type_attack]

            if attack_skills:
                skill = random.choice(attack_skills)

                # find the lowest hp
                sorted_opponents = sorted(opponents, key=lambda t: t.states.load("hp"))
                target = sorted_opponents[0]
                return skill.get_element_key(), target

        return
