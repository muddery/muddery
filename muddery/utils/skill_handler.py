"""
Skill handler handles a character's skills.

"""

from __future__ import print_function

import time
import traceback
from twisted.internet import task
from django.conf import settings
from evennia.utils import logger
from evennia.utils.utils import class_from_module
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
        ai_choose_skill_class = class_from_module(settings.AI_CHOOSE_SKILL)
        self.choose_skill = ai_choose_skill_class()
        
        self.owner = owner

        self.skills = {}
        if owner:
            self.skills = owner.db.skills

        self.gcd = GAME_SETTINGS.get("global_cd")
        self.auto_cast_skill_cd = GAME_SETTINGS.get("auto_cast_skill_cd")
        self.gcd_finish_time = 0
        
        # loop for auto cast skills
        self.loop = None

    def __del__(self):
        """
        Remove tickers.
        """
        if self.loop and self.loop.running:
            self.loop.stop()

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
            if self.owner.has_account:
                self.owner.show_status()

        # Notify the player
        if self.owner.has_account:
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
        
    def remove_all(self):
        """
        Remove all skills.
        
        It will be called when skills' owner will be deleted.
        """
        for skill in self.skills.values():
            skill.delete()
        self.skills = {}

    def cast_skill(self, skill_key, target):
        """
        Cast a skill.

        Args:
            skill_key: (string) skill's key.
            target: (object) skill's target.

        Returns:
            (dict) result of the skill
        """
        if not self.owner:
            return

        time_now = time.time()
        if time_now < self.gcd_finish_time:
            # In GCD.
            message = _("Global cooling down!")
            if self.owner.is_in_combat():
                self.owner.msg({"skill_cast": {"message": message}})
            else:
                self.owner.msg({"msg": message})
            return

        if skill_key not in self.skills:
            message = _("You do not have this skill.")
            if self.owner.is_in_combat():
                self.owner.msg({"skill_cast": {"message": message}})
            else:
                self.owner.msg({"alert": message})
            return

        skill = self.skills[skill_key]
        if not skill.cast_skill(target, passive=False):
            return

        if self.gcd > 0:
            # set GCD
            self.gcd_finish_time = time_now + self.gcd

        # send CD to the player
        cd = {"skill": skill_key,               # skill's key
              "cd": skill.cd,                   # skill's cd
              "gcd": self.gcd}

        self.owner.msg({"skill_cd": cd})
        return

    def auto_cast_skill(self):
        """
        Cast a new skill automatically.
        """
        if not self.owner:
            return

        if not self.owner.is_alive():
            return

        if not self.owner.ndb.combat_handler:
            # combat is finished, stop ticker
            if self.loop and self.loop.running:
                self.loop.stop()
            return

        # Choose a skill and the skill's target.
        result = self.choose_skill.choose(self.owner)
        if result:
            skill, target = result
            self.owner.ndb.combat_handler.prepare_skill(skill, self.owner, target)

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
                self.skills[skill].cast_skill(self.owner, passive=True)

    def start_auto_combat_skill(self):
        """
        Start auto cast skill.
        """
        if self.loop and self.loop.running:
            return

        # Cast a skill immediately
        # self.auto_cast_skill()

        # Set timer of auto cast.
        self.loop = task.LoopingCall(self.auto_cast_skill)
        self.loop.start(self.auto_cast_skill_cd)

    def stop_auto_combat_skill(self):
        """
        Stop auto cast skill.
        """
        if self.loop and self.loop.running:
            self.loop.stop()
