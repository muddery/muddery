
import json
from django.conf import settings
from muddery.server.utils import logger
from muddery.server.utils.utils import class_from_path


class CommandHandler(object):
    """
    Handler incoming commands.
    """
    def __init__(self, session_cmdset, account_cmdset, character_cmdset):
        super(CommandHandler, self).__init__()

        self.session_cmdset = session_cmdset
        self.account_cmdset = account_cmdset
        self.character_cmdset = character_cmdset

    def handler_command(self, session, raw_string):
        print("Receive command, %s: %s" % (session, raw_string))
        logger.log_info("Receive command, %s: %s" % (session, raw_string))

        # Parse JSON formated command.
        try:
            data = json.loads(raw_string)
        except Exception:
            # Command is not in JSON.
            logger.log_err("Can not parse command, %s: %s" % (session, raw_string))
            return

        print("data: %s" % data)
        print("type: %s" % type(data))

        command_key = data["cmd"]
        args = data["args"]
        # context default is None
        context = data.get("context")

        # Find the matching command in cmdset.
        # session commands
        command = self.session_cmdset.get(command_key)
        if command:
            command.func(session, args, context)
            return

        # account commands
        account = session.account
        if account:
            command = self.account_cmdset.get(command_key)
            if command:
                command.func(account, args, context)
                return

            # character commands
            character = account.get_puppet_obj()
            if character:
                command = self.character_cmdset.get(command_key)
                if command:
                    command.func(character, args, context)
                    return

        logger.log_err("Can not find command, %s: %s" % (session, raw_string))