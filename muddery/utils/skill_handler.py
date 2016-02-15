"""
Skill handler handles a character's skills.

"""

import time
import random
from django.conf import settings
from evennia import TICKER_HANDLER
from muddery.utils.builder import build_object
from muddery.utils.localized_strings_handler import LS
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

        # TICKER_HANDLER needs pk.
        self.pk = "SKILL"

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
            TICKER_HANDLER.remove(self)

    def get_all(self):
        """
        Get all skills.
        """
        return self.skills

    def learn_skill(self, skill):
        """
        Learn a new skill.

        Args:
            skill: (string) skill's key

        Returns:
            None
        """
        if not self.owner:
            return

        if skill in self.skills:
            self.owner.msg({"alert": LS("You have already learned this skill.")})
            return

        # Create skill object.
        skill_obj = build_object(skill)
        if not skill_obj:
            self.owner.msg({"alert": LS("Can not learn this skill.")})
            return

        # Store new skill.
        skill_obj.set_owner(self.owner)
        self.skills[skill] = skill_obj

        # If it is a passive skill, player's status may change.
        if skill_obj.passive:
            self.owner.refresh_data()

            # Notify the player
            if self.owner.has_player:
                self.owner.show_status()

        # Notify the player
        if self.owner.has_player:
            self.owner.show_skills()
            self.owner.msg({"msg": LS("You learned skill {c%s{n.") % skill_obj.get_name()})

    def has_skill(self, skill):
        """
        If the character has the skill or not.

        Args:
            skill: (string) skill's key

        Returns:
            None
        """
        return skill in self.skills

    def cast_skill(self, skill, target):
        """
        Cast a skill.

        Args:
            skill: (string) skill's key
            target: (object) skill's target

        Returns:
            (dict) result of the skill
        """
        if not self.owner:
            return

        if time.time() < self.gcd_finish_time:
            # In GCD.
            self.owner.msg({"msg": LS("This skill is not ready yet!")})
            return

        if skill not in self.skills:
            self.owner.msg({"alert": LS("You do not have this skill.")})
            return

        message = self.skills[skill].check_available()
        if message:
            # Skill is not available.
            self.owner.msg({"msg": message})
            return

        result, cd = self.skills[skill].cast_skill(target)

        if result:
            if self.owner.ndb.combat_handler:
                # send skill's result to the combat handler
                self.owner.ndb.combat_handler.set_skill_result(result)
            else:
                # TODO: send result to the target too!
                self.owner.msg({"skill_result": result})

        # set GCD
        if not cd:
            cd = {}

        cd["gcd"] = self.gcd
        if self.gcd > 0:
            self.gcd_finish_time = time.time() + self.gcd

        # send CD to the player
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
            TICKER_HANDLER.remove(self, self.auto_cast_skill_cd)
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
            self.cast_skill(skill, self.skill_target)

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
        TICKER_HANDLER.add(self, self.auto_cast_skill_cd, hook_key="auto_cast_skill")

    def stop_auto_combat_skill(self):
        """
        Stop auto cast skill.
        """
        self.can_auto_cast = False
        TICKER_HANDLER.remove(self, self.auto_cast_skill_cd)
