"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

import time
import importlib
from django.conf import settings
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.localized_strings_handler import LS
from muddery.utils.game_settings import GAME_SETTINGS


class MudderySkill(MudderyObject):
    """
    A skill of the character.
    """

    _skill_modues = {}

    @classmethod
    def load_skill_modules(cls):
        """
        Load all available skills.

        Returns:
            None
        """
        for module_name in settings.SKILL_MODULES:
            try:
                module = importlib.import_module(module_name)
                skills = [skill for skill in dir(module) if skill[0] != '_']

                for skill in skills:
                    cls._skill_modues[skill] = getattr(module, skill, None)
            except ImportError:
                logger.log_errmsg("Can not import skill module %s." % module_name)

    def at_object_creation(self):
        """
        Set default values.

        Returns:
            None
        """
        super(MudderySkill, self).at_object_creation()
        
        # set status
        self.db.owner = None
        self.db.cd_finish_time = 0
        self.db.is_default = False

    def set_default(self, is_default):
        """
        Set this skill as default skill.
        When skills in table default_skills changes, character's relative skills
        will change too.

        Args:
            is_default: (boolean) if the is default or not.
        """
        self.db.is_default = is_default

    def is_default(self):
        """
        Check if this skill is a default skill or not.

        Returns:
            (boolean) is default or not
        """
        return self.db.is_default

    def load_data(self):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(MudderySkill, self).load_data()

        # search skill function
        self.function_call = None
        if self.dfield.function in self._skill_modues:
            self.function_call = self._skill_modues[self.dfield.function]

        # set data
        self.effect = getattr(self.dfield, "effect", 0)
        self.cd = getattr(self.dfield, "cd", 0)
        self.passive = getattr(self.dfield, "passive", False)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.

        Args:
            caller: (object) command's caller

        Returns:
            commands: (list) a list of available commands
        """
        if self.passive:
            return

        commands = [{"name": LS("Cast"), "cmd": "castskill", "args": self.get_data_key()}]
        return commands

    def set_owner(self, owner):
        """
        Set the owner of the skill.

        Args:
            owner: (object) skill's owner

        Returns:
            None
        """
        self.db.owner = owner
    
        if not self.passive:
            # Set skill cd. Add gcd to new the skill.
            gcd = GAME_SETTINGS.get("global_cd")
            if gcd > 0:
                self.db.cd_finish_time = time.time() + gcd

    def cast_skill_manually(self, target):
        """
        Cast this skill manually. Can not cast passive skill in this way.

        Args:
            target: (object) skill's target

        Returns:
            result: (dict) skill's result
        """
        if self.passive:
            owner = self.db.owner
            if owner:
                owner.msg({"alert": LS("You can not cast a passive skill.")})
            return
    
        return self.cast_skill(target)

    def cast_skill(self, target):
        """
        Cast this skill.

        Args:
            target: (object) skill's target

        Returns:
            (result, cd):
                result: (dict) skill's result
                cd: (dice) skill's cd
        """
        owner = self.db.owner
        time_now = time.time()

        if not self.passive:
            if owner:
                gcd = getattr(owner, "gcd_finish_time", 0)
                if time_now < gcd:
                    owner.msg({"msg": LS("This skill is not ready yet!")})
                    return

            if time_now < self.db.cd_finish_time:
                # skill in CD
                if owner:
                    owner.msg({"msg": LS("This skill is not ready yet!")})
                return

        if not self.function_call:
            logger.log_errmsg("Can not find skill function: %s" % self.get_data_key())
            if owner:
                owner.msg({"msg": LS("Can not cast this skill!")})
            return

        result = {}
        cd = {}
        try:
            # call skill function
            result = self.function_call(owner, target, effect=self.effect)

            if not self.passive:
                # set cd
                time_now = time.time()
                if self.cd > 0:
                    self.db.cd_finish_time = time_now + self.cd

                cd = {"skill": self.get_data_key(), # skill's key
                      "cd": self.cd}                # global cd
        except Exception, e:
            ostring = "Can not cast skill %s: %s" % (self.get_data_key(), e)
            logger.log_tracemsg(ostring)
            if owner:
                owner.msg({"msg": LS("Can not cast this skill!")})
            return

        return result, cd

    def check_available(self):
        """
        Check this skill.

        Returns:
            message: (string) If the skill is not available, returns a string of reason.
                     If the skill is available, return "".
        """
        if self.passive:
            return LS("This is a passive skill!")

        if self.is_cooling_down():
            return LS("This skill is not ready yet!")

        return ""

    def is_available(self):
        """
        If this skill is available.
        """
        return self.check_available() == ""

    def is_cooling_down(self):
        """
        If this skill is cooling down.
        """
        if self.cd > 0:
            if self.db.cd_finish_time:
                if time.time() < self.db.cd_finish_time:
                    return True
        return False

    def get_remain_cd(self):
        """
        Get skill's CD.

        Returns:
            (float) Remain CD in seconds.
        """
        remain_cd = self.db.cd_finish_time - time.time()
        if remain_cd < 0:
            remain_cd = 0
        return remain_cd