"""
Skill handler handles a character's skills.

"""

import time
import random
from django.conf import settings
from evennia.utils import logger
from muddery.combat.base_combat_handler import CStatus
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS

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
        
        skills = [caller.db.skills[skill] for skill in caller.db.skills if caller.db.skills[skill].is_available(passive=False)]
        if not skills:
            return

        team = caller.get_team()
        chars = combat.get_combat_characters()
        # teammates = [c for c in characters if c.get_team() == team]
        opponents = [c["char"] for c in chars if c["status"] == CStatus.ACTIVE and c["char"].get_team() != team]

        if caller.prop.hp < caller.prop.max_hp / 2:
            # heal self
            heal_skills = [skill for skill in skills if skill.main_type == cls.type_heal]
            if not heal_skills and caller.prop.hp < caller.prop.max_hp / 4:
                heal_skills = [skill for skill in skills if skill.sub_type == cls.type_heal]
                
            if heal_skills:
                skill = random.choice(heal_skills)
                target = caller
                return skill.get_data_key(), target
        
        if opponents:
            # attack opponents
            attack_skills = [skill for skill in skills if skill.main_type == cls.type_attack]
            if not attack_skills:
                attack_skills = [skill for skill in skills if skill.sub_type == cls.type_attack]

            if attack_skills:
                skill = random.choice(attack_skills)

                # find the lowest hp
                sorted_opponents = sorted(opponents, key=lambda t:t.prop.hp)
                target = sorted_opponents[0]
                return skill.get_data_key(), target

        return
