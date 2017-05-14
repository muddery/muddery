"""
Skill handler handles a character's skills.

"""

import time
import random
from django.conf import settings
from evennia import TICKER_HANDLER
from muddery.utils.builder import build_object
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS


class SkillHandler(object):
    """
    Skill handler handles a character's skills.
    """

    def __init__(self, owner):
        """
        Initialize handler.
        """
        self.owner = owner

        self.skills = {}
        if owner:
            self.skills = owner.db.skills

        self.gcd = GAME_SETTINGS.get("global_cd")
        self.auto_cast_skill_cd = GAME_SETTINGS.get("auto_cast_skill_cd")
        self.can_auto_cast = False
        self.skill_target = None
        self.gcd_finish_time = 0

    def __del__(self):
        """
        Remove tickers.
        """
        if self.can_auto_cast:
            TICKER_HANDLER.remove(callback=self.owner.auto_cast_skill)

    def get_all(self):
        """
        Get all skills.
        """
        return self.skills

    def learn_skill(self, skill_key, is_default=False):
        """
        Learn a new skill.

        Args:
            skill_key: (string) skill's key
            is_default: (boolean) if it is a default skill

        Returns:
            (boolean) learned skill
        """
        if not self.owner:
            return False

        if skill_key in self.skills:
            self.owner.msg({"msg": _("You have already learned this skill.")})
            return False

        # Create skill object.
        skill_obj = build_object(skill_key)
        if not skill_obj:
            self.owner.msg({"msg": _("Can not learn this skill.")})
            return False

        # set default
        if is_default:
            skill_obj.set_default(is_default)

        # Store new skill.
        skill_obj.set_owner(self.owner)
        self.skills[skill_key] = skill_obj

        # If it is a passive skill, player's status may change.
        if skill_obj.passive:
            self.owner.refresh_data()

            # Notify the player
            if self.owner.has_player:
                self.owner.show_status()

        # Notify the player
        if self.owner.has_player:
            self.owner.show_skills()
            self.owner.msg({"msg": _("You learned skill {c%s{n.") % skill_obj.get_name()})

        return True

    def has_skill(self, skill):
        """
        If the character has the skill or not.

        Args:
            skill: (string) skill's key

        Returns:
            None
        """
        return skill in self.skills

    def cast_skill(self, skill_key, target):
        """
        Cast a skill.

        Args:
            skill_key: (string) skill's key
            target: (object) skill's target

        Returns:
            (dict) result of the skill
        """
        if not self.owner:
            return

        if time.time() < self.gcd_finish_time:
            # In GCD.
            self.owner.msg({"msg": _("This skill is not ready yet!")})
            return

        if skill_key not in self.skills:
            self.owner.msg({"alert": _("You do not have this skill.")})
            return

        skill = self.skills[skill_key]

        message = skill.check_available()
        if message:
            # Skill is not available.
            self.owner.msg({"msg": message})
            return

        skill.cast_skill(target)

        if self.gcd > 0:
            # set GCD
            self.gcd_finish_time = time.time() + self.gcd

        # send CD to the player
        cd = {"skill": skill.get_data_key(),    # skill's key
              "cd": skill.cd,                   # skill's cd
              "gcd": self.gcd}

        self.owner.msg({"skill_cd": cd})

        return

    def auto_cast_skill(self):
        """
        Cast a new skill automatically.
        """
        if not self.can_auto_cast:
            return

        if not self.owner:
            return

        if not self.owner.ndb.combat_handler:
            # combat is finished, stop ticker
            TICKER_HANDLER.remove(self.auto_cast_skill_cd, self.owner.auto_cast_skill)
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
        if skill:
            self.owner.ndb.combat_handler.prepare_skill(skill, self.owner, self.skill_target)

    def get_available_skills(self):
        """
        Get available skills without cd.
        """
        skills = [skill for skill in self.skills if self.skills[skill].is_available()]
        return skills

    def get_passive_skills(self):
        """
        Get all passive skills.
        """
        skills = [skill for skill in self.skills if self.skills[skill].passive]
        return skills

    def cast_passive_skills(self):
        """
        Cast all passive skills.
        """
        for skill in self.skills:
            if self.skills[skill].passive:
                self.skills[skill].cast_skill(None)

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
        self.can_auto_cast = True

        # Cast a skill immediately
        self.auto_cast_skill()

        # Set timer of auto cast.
        TICKER_HANDLER.add(self.auto_cast_skill_cd, self.owner.auto_cast_skill)

    def stop_auto_combat_skill(self):
        """
        Stop auto cast skill.
        """
        self.can_auto_cast = False
        TICKER_HANDLER.remove(self.auto_cast_skill_cd, self.owner.auto_cast_skill)
