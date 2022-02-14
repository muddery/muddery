
import json
import traceback

from muddery.server.utils.logger import logger


class CommandHandler(object):
    """
    Handler incoming commands.
    """
    def __init__(self, session_cmdset, account_cmdset, character_cmdset):
        super(CommandHandler, self).__init__()

        self.session_cmdset = session_cmdset
        self.account_cmdset = account_cmdset
        self.character_cmdset = character_cmdset

    async def handler_command(self, session, raw_string):
        logger.log_debug("[Receive command][%s]%s" % (session, raw_string))

        # Parse JSON formated command.
        try:
            data = json.loads(raw_string)
        except Exception:
            # Command is not in JSON.
            logger.log_err("Can not parse command, %s: %s" % (session, raw_string))
            return

        command_key = data["cmd"]
        args = data["args"]

        # Find the matching command in cmdset.
        # session commands
        command = self.session_cmdset.get(command_key)
        caller = session

        if not command:
            account = session.account
            if account:
                command = self.account_cmdset.get(command_key)
                caller = account

                if not command:
                    character = session.account.get_puppet_obj()
                    if character:
                        command = self.character_cmdset.get(command_key)
                        caller = character

        if command:
            try:
                await command.func(caller, args)
            except Exception as e:
                logger.log_err("Run command error, %s: %s %s" % (session, raw_string, e))
            return
        else:
            logger.log_err("Can not find command, %s: %s" % (session, raw_string))