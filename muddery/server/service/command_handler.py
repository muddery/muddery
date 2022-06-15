
import json
import traceback

from muddery.server.utils.logger import logger
from muddery.server.commands.commands import Session, Account, Character


class CommandHandler(object):
    """
    Handler incoming commands.
    """
    def __init__(self, session_cmdset, account_cmdset, character_cmdset):
        super(CommandHandler, self).__init__()

        self.session_cmdset = session_cmdset
        self.account_cmdset = account_cmdset
        self.character_cmdset = character_cmdset

    def parse_command(self, raw_string):
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

    async def handler_command(self, session, command_key, args):
        # Find the matching command in cmdset.

        caller = None

        # session commands
        func = Session.get(command_key)
        if func:
            caller = session
            await func(caller, args)
        else:
            command = self.session_cmdset.get(command_key)

            if command:
                caller = session
            else:
                account = session.account
                if account:
                    command = self.account_cmdset.get(command_key)

                    if command:
                        caller = account
                    else:
                        character = session.account.get_puppet_obj()
                        if character:
                            command = self.character_cmdset.get(command_key)
                            caller = character

            if command:
                await command.process(caller, args)
            else:
                logger.log_err("Can not find command, %s: %s" % (session, command_key))
                await session.msg({"error": "Can not find command: %s" % command_key})
