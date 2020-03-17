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
    def choose(self, caller):
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

        skill = random.choice(skills)
        target = random.choice(opponents)
        return skill.get_data_key(), target
