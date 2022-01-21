"""
Skills

Each skill is a skill object stored in the character. The skill object stores all data and
actions of a skill.

"""

import re, traceback
from muddery.server.utils.localized_strings_handler import _
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.mappings.element_set import ELEMENT


class MudderySkill(ELEMENT("MATTER")):
    """
    A skill of the character.
    """
    element_type = "SKILL"
    element_name = "Skill"
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

    async def at_element_setup(self, first_time):
        """
        Set data_info to the object.

        Returns:
            None
        """
        await super(MudderySkill, self).at_element_setup(first_time)

        # set data
        self.function = self.const.function
        self.cd = self.const.cd if self.const.cd else 0
        self.passive = self.const.passive if self.const.passive else False
        self.main_type = self.const.main_type
        self.sub_type = self.const.sub_type
        
        message_model = self.const.message
        self.message_model = self.msg_escape.sub(self.escape_fun, message_model)

    async def get_available_commands(self, caller):
        """
        This returns a list of available commands.

        Args:
            caller: (object) command's caller

        Returns:
            commands: (list) a list of available commands
        """
        if self.passive:
            return []

        commands = [{"name": _("Cast"), "cmd": "cast_skill", "args": self.get_element_key()}]
        return commands

    async def cast(self, caller, target):
        """
        Cast this skill.

        Args:
            target: (object) skill's target.

        Returns:
            skill_cast: (dict) skill's result
        """
        case_message = await self.cast_message(caller, target)

        # traceback.print_stack()
        results = await self.do_skill(caller, target)

        # set message
        skill_cast = {
            "skill": self.get_element_key(),
            "main_type": self.main_type,
            "sub_type": self.sub_type,
            "cast": case_message,
        }

        if caller:
            skill_cast["caller"] = caller.get_id()
            skill_cast["status"] = {
                caller.get_id(): await caller.get_combat_status(),
            }

        if target:
            skill_cast["target"] = target.get_id()
            skill_cast["status"][target.get_id()] = await target.get_combat_status()

        if results:
            skill_cast["result"] = " ".join(results)

        return skill_cast
        
    async def do_skill(self, caller, target):
        """
        Do this skill.
        """
        # call skill function
        return await STATEMENT_HANDLER.do_skill(self.function, caller, target)

    async def is_available(self, caller, passive):
        """
        If this skill is available.

        Args:
            passive: (boolean) cast a passive skill.

        Returns:
            (boolean) available or not.
        """
        if not passive and self.passive:
            return False

        return True

    async def cast_message(self, caller, target):
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
            values = {"n": self.get_name(),
                      "c": caller_name,
                      "t": target_name}
            message = self.message_model % values

        return message

    def is_passive(self):
        """
        Is a passive skill.
        :return:
        """
        return self.passive

    def get_cd(self):
        """
        Get this skill's CD
        :return:
        """
        if self.passive:
            return 0

        return self.cd

    def get_appearance(self):
        """
        The common appearance for all players.
        """
        info = super(MudderySkill, self).get_appearance()
        info["passive"] = self.passive
        info["cd"] = self.get_cd()

        return info
