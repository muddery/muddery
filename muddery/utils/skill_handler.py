"""
Skill handler handles a character's skills.

"""

import traceback
import random
from django.conf import settings
from evennia.utils import logger
from evennia.utils.utils import lazy_property
from evennia import TICKER_HANDLER
from muddery.utils.exception import MudderyError
from muddery.utils.builder import build_object
from muddery.utils.localized_strings_handler import LS


class SkillHandler(object):
    """
    Skill handler handles a character's skills.
    """

    def __init__(self, owner):
        """
        Initialize handler.
        """
        self.owner = owner
        self.skills = owner.db.skills
        
        # TICKER_HANDLER needs pk.
        self.pk = "SKILL"
        
        # always begin with GCD
        self.GLOBAL_COOLING_DOWN = True
        TICKER_HANDLER.add(self, settings.GLOBAL_CD, hook_key="global_cooled_down")

        self.AUTO_CAST_SKILL = False
        self.skill_target = None


    def __del__(self):
        """
        Remove tickers.
        """
        if self.GLOBAL_COOLING_DOWN or self.AUTO_CAST_SKILL:
            TICKER_HANDLER.remove(self)


    def learn_skill(self, skill):
        """
        Learn a new skill.
        """
        if not self.owner:
            return

        if skill in self.skills:
            self.msg({"alert":LS("You have already learned this skill.")})
            return

        # Create skill object.
        skill_obj = build_object(skill)
        if not skill_obj:
            self.owner.msg({"alert":LS("Can not learn this skill.")})
            return

        # Store new skill.
        skill_obj.set_owner(self.owner)
        self.skills[skill] = skill_obj

        if self.owner.has_player:
            self.owner.show_skills()
            self.owner.msg({"msg":LS("You learned skill {c%s{n.") % skill_obj.get_name()})


    def has_skill(self, skill):
        """
        If the character has the skill or not.
        """
        return skill in self.skills


    def cast_skill_manually(self, skill, target):
        """
        Cast a skill positively.
        """
        if not skill in self.skills:
            self.msg({"alert":LS("You do not have this skill.")})
            return

        return self.skills[skill].cast_skill_manually(target)


    def cast_combat_skill(self, skill, target):
        """
        Cast a skill in combat.
        """
        if not self.owner:
            return

        if not self.owner.ndb.combat_handler:
            # Onwer is not in combat.
            return

        if self.GLOBAL_COOLING_DOWN:
            # In GCD.
            self.owner.msg({"msg":LS("This skill is not ready yet!")})
            return

        if self.skills[skill].is_cooling_down():
            # Skill is cooling down.
            self.owner.msg({"msg":LS("This skill is not ready yet!")})
            return

        # Cast skill.
        result = self.owner.ndb.combat_handler.cast_skill_manually(skill, self.owner.dbref, target)
        if result:
            # Cast successed, set GCD
            if settings.GLOBAL_CD > 0:
                self.GLOBAL_COOLING_DOWN = True
                
                # Set timer of GCD.
                TICKER_HANDLER.add(self, settings.GLOBAL_CD, hook_key="global_cooled_down")

        return result


    def global_cooled_down(self):
        """
        GCD finished.
        """
        self.GLOBAL_COOLING_DOWN = False
        
        # Remove the timer.
        TICKER_HANDLER.remove(self, settings.GLOBAL_CD)


    def auto_cast_skill(self):
        """
        Cast a new skill automatically.
        """
        if not self.AUTO_CAST_SKILL:
            return

        if not self.owner:
            return

        if not self.owner.ndb.combat_handler:
            # combat is finished, stop ticker
            TICKER_HANDLER.remove(self, settings.AUTO_CAST_SKILL_CD)
            return

        # Get target.
        choose_new_target = True
        if self.skill_target:
            if self.skill_target.is_alive():
                choose_new_target = False

        if choose_new_target:
            self.skill_target = self.choose_skill_target()

        if not self.skill_target:
            # No target.
            return

        # Get available skills.
        available_skills = self.get_available_skills()
        if not available_skills:
            # No available skill.
            return

        # Random chooses a skill.
        skill = random.choice(available_skills)
        self.cast_combat_skill(skill, self.skill_target.dbref)


    def get_available_skills(self):
        """
        Get available skills without cd.
        """
        skills = [skill for skill in self.skills if not self.skills[skill].is_cooling_down()]
        return skills


    def choose_skill_target(self):
        """
        Choose a target automatically.
        """
        if not self.owner:
            return

        if not self.owner.ndb.combat_handler:
            "Not in combat."
            return

        # Get all combat characters.
        characters = self.owner.ndb.combat_handler.get_all_characters()
        for character in characters:
            if character.is_alive() and character.dbref != self.owner.dbref:
                return character

        return


    def start_auto_combat_skill(self):
        """
        Start auto cast skill.
        """
        self.AUTO_CAST_SKILL = True

        # Cast a skill immediately
        self.auto_cast_skill()

        # Set timer of auto cast.
        TICKER_HANDLER.add(self, settings.AUTO_CAST_SKILL_CD, hook_key="auto_cast_skill")


    def stop_auto_combat_skill(self):
        """
        Stop auto cast skill.
        """
        self.AUTO_CAST_SKILL = False
        TICKER_HANDLER.remove(self, settings.AUTO_CAST_SKILL_CD)
