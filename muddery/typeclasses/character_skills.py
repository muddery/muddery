"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

import time, re
from django.conf import settings
from evennia.utils import logger
from muddery.typeclasses.objects import MudderyObject
from muddery.utils.localized_strings_handler import _
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.mappings.typeclass_set import typeclass_mapping, TYPECLASS


@typeclass_mapping("COMMON_OBJECT")
class MudderySkill(TYPECLASS("BASE_OBJECT")):
    """
    A skill of the character.
    """
    msg_escape = re.compile(r'%[%|n|c|t]')

    @staticmethod
    def escape_fun(word):
        """
        Change escapes to target words.
        """
        escape_word = word.group()
        char = escape_word[1]
        if char == "%":
            return char
        else:
            return "%(" + char + ")s"

    def at_object_creation(self):
        """
        Set default values.

        Returns:
            None
        """
        super(MudderySkill, self).at_object_creation()
        
        # set status
        if not self.attributes.has("owner"):
            self.db.owner = None
        if not self.attributes.has("cd_finish_time"):
            self.db.cd_finish_time = 0
        if not self.attributes.has("is_default"):
            self.db.is_default = False

    def set_default(self, is_default):
        """
        Set this skill as the character's default skill.
        When skills in table default_skills changes, character's relative skills
        will change too.

        Args:
            is_default: (boolean) if the is default or not.
        """
        self.db.is_default = is_default

    def is_default(self):
        """
        Check if this skill is the character's default skill.

        Returns:
            (boolean) is default or not
        """
        return self.db.is_default

    def after_data_loaded(self):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(MudderySkill, self).after_data_loaded()

        # set data
        self.function = getattr(self.dfield, "function", "")
        self.cd = getattr(self.dfield, "cd", 0)
        self.passive = getattr(self.dfield, "passive", False)
        self.main_type = getattr(self.dfield, "main_type", "")
        self.sub_type = getattr(self.dfield, "sub_type", "")
        
        message_model = getattr(self.dfield, "message", "")
        self.message_model = self.msg_escape.sub(self.escape_fun, message_model)

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

        commands = [{"name": _("Cast"), "cmd": "castskill", "args": self.get_data_key()}]
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

    def cast_skill(self, target, passive):
        """
        Cast this skill.

        Args:
            target: (object) skill's target.
            passive: (boolean) cast a passive skill.

        Returns:
            (result, cd):
                result: (dict) skill's result
                cd: (dict) skill's cd
        """
        owner = self.db.owner

        message = {}
        not_available = self.check_available(passive)
        if not_available:
            message = {"cast": not_available}
        else:
            results = self.do_skill(target)

            if not passive:
                # set message
                message = {"caller": owner.dbref,
                           "skill": self.get_data_key(),
                           "cast": self.cast_message(target)}

                if target:
                    message["target"] = target.dbref

                if results:
                    message["result"] = " ".join(results)

                # set status
                status = {}
                if owner.is_in_combat():
                    for char in owner.ndb.combat_handler.get_all_characters():
                        status[char.dbref] = char.get_combat_status()
                elif owner.location:
                    status[owner.dbref] = owner.get_combat_status()
                message["status"] = status

        if not passive and message:
            # send message
            if owner.is_in_combat():
                owner.ndb.combat_handler.msg_all({"skill_cast": message})
            elif owner.location:
                owner.location.msg_contents({"skill_cast": message})

        return True
        
    def do_skill(self, target):
        """
        Do this skill.
        """
        # set cd
        if not self.passive:
            # set cd
            time_now = time.time()
            if self.cd > 0:
                self.db.cd_finish_time = time_now + self.cd

        # call skill function
        return STATEMENT_HANDLER.do_skill(self.function, self.db.owner, target)

    def check_available(self, passive):
        """
        Check this skill.
        
        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            message: (string) If the skill is not available, returns a string of reason.
                     If the skill is available, return "".
        """
        if not passive and self.passive:
            return _("{c%s{n is a passive skill!") % self.get_name()

        if self.is_cooling_down():
            return _("{c%s{n is not ready yet!") % self.get_name()

        return ""

    def is_available(self, passive):
        """
        If this skill is available.
        
        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            (boolean) available or not.
        """
        if not passive and self.passive:
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

    def cast_message(self, target):
        """
        Create skill's result message.
        """
        caller_name = ""
        target_name = ""
        message = ""

        if self.db.owner:
            caller_name = self.db.owner.get_name()

        if target:
            target_name = target.get_name()

        if self.message_model:
            values = {"n": self.name,
                      "c": caller_name,
                      "t": target_name}
            message = self.message_model % values

        return message

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(MudderySkill, self).get_appearance(caller)
        
        info["passive"] = self.passive
        info["cd_remain"] = self.get_remain_cd()

        return info
