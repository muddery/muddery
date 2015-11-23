"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

import time
import traceback
import importlib
from django.conf import settings
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.exception import MudderyError
from muddery.utils.localized_strings_handler import LS


class MudderySkill(MudderyObject):
    """
    A skill of the character.
    """

    _skill_modues = {}

    @classmethod
    def load_skill_modules(cls):
        """
        Load all available skills.
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
        """
        super(MudderySkill, self).at_object_creation()
        
        # set status
        self.db.owner = None
        self.db.cd_end_time = 0


    def load_data(self):
        """
        Set data_info to the object.
        """
        super(MudderySkill, self).load_data()

        # search skill function
        self.function_call = None
        if self.function in self._skill_modues:
            self.function_call = self._skill_modues[self.function]


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        if self.passive:
            return

        commands = [{"name":LS("CAST"), "cmd":"castskill", "args":self.get_info_key()}]
        return commands


    def set_owner(self, owner):
        """
        Set the owner of the skill.
        """
        self.db.owner = owner
    
        if self.passive:
            # Cast passive skill when a character owns this skill.
            self.cast_skill()
        else:
            # Set skill cd.
            if self.cd > 0:
                self.db.cd_end_time = time.time() + self.cd


    def cast_skill_manually(self, target):
        """
        Cast this skill manually. Can not cast passive skill in this way.
        """
        if self.passive:
            owner = self.db.owner
            if owner:
                owner.msg({"alert":LS("You can not cast a passive skill.")})
            return
    
        return self.cast_skill(target)


    def cast_skill(self, target):
        """
        Cast this skill.
        """
        owner = self.db.owner

        if self.cd > 0:
            # skill is in cd.
            if time.time() < self.db.cd_end_time:
                if owner:
                    owner.msg({"msg":LS("This skill is not ready yet!")})
                return

        if not self.function_call:
            logger.log_errmsg("Can not find skill function: %s" % self.get_info_key())
            if owner:
                owner.msg({"msg": LS("Can not cast this skill!")})
            return

        try:
            # call skill function
            result = self.function_call(owner, target, effect=self.effect)

            # set cd
            if self.cd > 0:
                self.db.cd_end_time = time.time() + self.cd

            cd_info = {"skill": self.get_info_key(),    # skill's key
                       "cd": self.cd,                   # skill's cd
                       "gcd": settings.GLOBAL_CD}       # global cd
        except Exception, e:
            ostring = "Can not cast skill %s: %s" % (self.get_info_key(), e)
            logger.log_errmsg(ostring)
            print traceback.format_exc()
            if owner:
                owner.msg({"msg": LS("Can not cast this skill!")})
            return

        return {"result": result,
                "cd_info": cd_info}


    def is_cooling_down(self):
        """
        If this skill is cooling down.
        """
        if self.cd > 0:
            if self.db.cd_end_time:
                if time.time() < self.db.cd_end_time:
                    return True
        return False
