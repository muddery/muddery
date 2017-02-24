"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

import time
import ast
from django.conf import settings
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.localized_strings_handler import LS
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.statements.statement_handler import STATEMENT_HANDLER


class MudderySkill(MudderyObject):
    """
    A skill of the character.
    """

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

        # set data
        self.function = getattr(self.dfield, "function", "")
        self.cd = getattr(self.dfield, "cd", 0)
        self.passive = getattr(self.dfield, "passive", False)
        self.message = getattr(self.dfield, "message", "")

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
            if time_now < self.db.cd_finish_time:
                # skill in CD
                if owner:
                    owner.msg({"msg": LS("This skill is not ready yet!")})
                return

        # call skill function
        print("skill_key: %s" % self.get_data_key())
        STATEMENT_HANDLER.do_skill(self.function, owner, target,
                                   key=self.get_data_key(), name=self.get_name(),
                                   message=self.message)

        if not self.passive:
            # set cd
            time_now = time.time()
            if self.cd > 0:
                self.db.cd_finish_time = time_now + self.cd

        return

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
        if self.passive:
            return False

        if self.is_cooling_down():
            return False

        return True

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
