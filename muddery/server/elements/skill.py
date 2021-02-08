"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

import time, re
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.mappings.element_set import ELEMENT


class MudderySkill(ELEMENT("OBJECT")):
    """
    A skill of the character.
    """
    element_key = "SKILL"
    element_name = _("Skill", "elements")
    model_name = "skills"

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

        self._is_default = False

        # Set skill cd. Add gcd to new the skill.
        gcd = GAME_SETTINGS.get("global_cd")
        if gcd > 0:
            self.state.save("cd_finish_time", time.time() + gcd)

    def at_init(self):
        """
        Load the skill's data.
        """
        super(MudderySkill, self).at_init()

        self._is_default = self.state.load("is_default", False)

    def set_default(self, is_default):
        """
        Set this skill as the character's default skill.
        When skills in table default_skills changes, character's relative skills
        will change too.

        Args:
            is_default: (boolean) if the is default or not.
        """
        self._is_default = is_default
        self.state.save("is_default", is_default)

    def is_default(self):
        """
        Check if this skill is the character's default skill.

        Returns:
            (boolean) is default or not
        """
        return self._is_default

    def after_data_loaded(self):
        """
        Set data_info to the object.

        Returns:
            None
        """
        super(MudderySkill, self).after_data_loaded()

        # set data
        self.function = getattr(self.system, "function", "")
        self.cd = getattr(self.system, "cd", 0)
        self.passive = getattr(self.system, "passive", False)
        self.main_type = getattr(self.system, "main_type", "")
        self.sub_type = getattr(self.system, "sub_type", "")
        
        message_model = getattr(self.system, "message", "")
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
            return []

        commands = [{"name": _("Cast"), "cmd": "cast_skill", "args": self.get_data_key()}]
        return commands

    def cast(self, caller, target):
        """
        Cast this skill.

        Args:
            target: (object) skill's target.

        Returns:
            skill_cast: (dict) skill's result
        """
        skill_cast = {}
        not_available = self.get_available_message(caller)
        if not_available:
            skill_cast = {"cast": not_available}
        else:
            case_message = self.cast_message(caller, target)
            results = self.do_skill(caller, target)

            # set message
            skill_cast = {
                "skill": self.get_data_key(),
                "main_type": self.main_type,
                "sub_type": self.sub_type,
                "cast": case_message,
            }

            if caller:
                skill_cast["caller"] = caller.dbref
                skill_cast["status"] = {
                    caller.dbref: caller.get_combat_status(),
                }

            if target:
                skill_cast["target"] = target.dbref
                skill_cast["status"][target.dbref] = target.get_combat_status()

            if results:
                skill_cast["result"] = " ".join(results)

        return skill_cast
        
    def do_skill(self, caller, target):
        """
        Do this skill.
        """
        # set cd
        if not self.passive:
            # set cd
            time_now = time.time()
            if self.cd > 0:
                self.state.save("cd_finish_time", time_now + self.cd)

        # call skill function
        return STATEMENT_HANDLER.do_skill(self.function, caller, target)

    def get_available_message(self, caller):
        """
        Check this skill.

        Returns:
            message: (string) If the skill is not available, returns a string of reason.
                     If the skill is available, return "".
        """
        if self.is_cooling_down():
            return _("{C%s{n is not ready yet!") % self.get_name()

        return ""

    def is_available(self, caller, passive):
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
            cd_finish_time = self.state.load("cd_finish_time", 0)
            if cd_finish_time:
                if time.time() < cd_finish_time:
                    return True
        return False

    def get_remain_cd(self):
        """
        Get skill's CD.

        Returns:
            (float) Remain CD in seconds.
        """
        cd_finish_time = self.state.load("cd_finish_time", 0)
        remain_cd = cd_finish_time - time.time()
        if remain_cd < 0:
            remain_cd = 0
        return remain_cd

    def cast_message(self, caller, target):
        """
        Create skill's result message.
        """
        caller_name = ""
        target_name = ""
        message = ""

        if caller:
            caller_name = caller.get_name()

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
