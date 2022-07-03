
import json
import traceback

from muddery.server.utils.logger import logger
from muddery.server.commands.command_set import SessionCmd, AccountCmd, CharacterCmd


class CommandHandler(object):
    """
    Handler incoming commands.
    """
    @classmethod
    def parse_command(cls, raw_string):
        """
        Parse JSON formatted command.
        """
        try:
            data = json.loads(raw_string)
        except Exception:
            # Command is not in JSON.
            logger.log_err("Can not parse command, %s: %s" % (raw_string))
            return

        return data["cmd"], data["args"]

    @classmethod
    async def handler_command(cls, session, command_key, args):
        # Find the matching command in cmdset.

        caller = None

        # session commands
        func = SessionCmd.get(command_key)

        if func:
            caller = session
        else:
            account = session.account
            if session.account:
                func = AccountCmd.get(command_key)

                if func:
                    caller = account
                else:
                    character = session.account.get_puppet_obj()
                    if character:
                        func = CharacterCmd.get(command_key)

                        if func:
                            caller = character

        if func:
            await func(caller, args)
        else:
            logger.log_err("Can not find command, %s: %s" % (session, command_key))
            await session.msg({"error": "Can not find command: %s" % command_key})
