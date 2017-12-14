"""
Skill handler handles a character's skills.

"""

from __future__ import print_function

import time
import random
from django.conf import settings
from evennia.utils import logger
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
        
        skills = [caller.db.skills[skill] for skill in caller.db.skills if caller.db.skills[skill].is_available()]
        if not skills:
            return

        team = caller.get_team()
        characters = combat.get_all_characters()
        # teammates = [c for c in characters if c.get_team() == team]
        opponents = [c for c in characters if c.get_team() != team]

        skill = random.choice(skills)
        target = caller
        return skill.get_data_key(), target
